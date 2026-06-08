"""Greenhouse happy path pipeline (v1)."""

from __future__ import annotations

import asyncio
import json
import logging
import time
from collections import deque
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from r3_ch.ats.greenhouse_client import GreenhouseClient
from r3_ch.config import (
    GREENHOUSE_ACTIVE_SLUGS_PATH,
    GREENHOUSE_INVALID_SLUGS_PATH,
    GREENHOUSE_LAST_RUN_PATH,
    GREENHOUSE_PROCESSED_SLUGS_PATH,
    GREENHOUSE_RATE_LIMIT_PER_SEC,
    GREENHOUSE_SLUGS_PATH,
    GREENHOUSE_STATE_DIR,
    GREENHOUSE_MAX_CONCURRENCY,
    OUTPUT_MASTER_MATCHES_PATH,
    OUTPUT_MATCHES_PATH,
)
from r3_ch.filters.eligibility import evaluate_eligibility
from r3_ch.filters.role_filter import match_ai_role_keywords
from r3_ch.state.slug_state_store import GreenhouseSlugStateStore, SlugState
from r3_ch.storage.master_store import GreenhouseMasterStore

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class SlugProcessResult:
    slug: str
    status: str
    error: str | None
    matched_records: list[dict[str, Any]]


def _extract_location_name(job: dict[str, Any]) -> str | None:
    location = job.get("location")
    if isinstance(location, dict):
        value = location.get("name")
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None


def _make_funnel(total_slugs: int) -> dict[str, int]:
    return {
        "total_slugs_considered": total_slugs,
        "portal_active": 0,
        "portal_not_found": 0,
        "portal_error": 0,
        "active_with_ai_roles": 0,
        "active_without_ai_roles": 0,
        "ai_roles_total": 0,
        "eligible_ok": 0,
        "eligible_not_eligible": 0,
        "eligible_unknown": 0,
    }


class AsyncRateLimiter:
    """Simple sliding-window limiter: max N acquisitions per second."""

    def __init__(self, max_per_second: int) -> None:
        self._max_per_second = max_per_second
        self._timestamps: deque[float] = deque()
        self._lock = asyncio.Lock()

    async def acquire(self) -> None:
        while True:
            async with self._lock:
                now = time.monotonic()
                while self._timestamps and now - self._timestamps[0] >= 1.0:
                    self._timestamps.popleft()

                if len(self._timestamps) < self._max_per_second:
                    self._timestamps.append(now)
                    return

                wait_for = 1.0 - (now - self._timestamps[0])
            await asyncio.sleep(max(wait_for, 0.001))


def _build_state_store() -> GreenhouseSlugStateStore:
    return GreenhouseSlugStateStore(
        source_slugs_path=GREENHOUSE_SLUGS_PATH,
        active_slugs_path=GREENHOUSE_ACTIVE_SLUGS_PATH,
        invalid_slugs_path=GREENHOUSE_INVALID_SLUGS_PATH,
        processed_slugs_path=GREENHOUSE_PROCESSED_SLUGS_PATH,
        last_run_path=GREENHOUSE_LAST_RUN_PATH,
    )


async def _process_slug(
    slug: str,
    target_location: str,
    client: GreenhouseClient,
    semaphore: asyncio.Semaphore,
    rate_limiter: AsyncRateLimiter,
) -> SlugProcessResult:
    async with semaphore:
        await rate_limiter.acquire()
        fetch_result = await client.fetch_jobs(slug)

    logger.info("Processing slug=%s status=%s", slug, fetch_result.status)
    if fetch_result.status != "active":
        return SlugProcessResult(
            slug=slug,
            status=fetch_result.status,
            error=fetch_result.error,
            matched_records=[],
        )

    matches: list[dict[str, Any]] = []
    for job in fetch_result.jobs:
        title = str(job.get("title", ""))
        content = str(job.get("content", ""))
        matched_keywords = match_ai_role_keywords(title=title, content=content)
        if not matched_keywords:
            continue

        location_raw = _extract_location_name(job)
        eligibility = evaluate_eligibility(location_raw)
        matches.append(
            {
                "slug": slug,
                "job_id": job.get("id"),
                "title": title,
                "updated_at": job.get("updated_at"),
                "location_raw": location_raw,
                "eligibility": eligibility,
                "absolute_url": job.get("absolute_url"),
                "matched_keywords": matched_keywords,
                "target_location": target_location,
            }
        )

    return SlugProcessResult(
        slug=slug,
        status="active",
        error=None,
        matched_records=matches,
    )


def _apply_state_transitions(previous: SlugState, results: list[SlugProcessResult]) -> tuple[SlugState, dict[str, list[str]]]:
    active = set(previous.active)
    invalid = set(previous.invalid)
    processed = set(previous.processed)

    for result in results:
        processed.add(result.slug)
        if result.status == "active":
            active.add(result.slug)
            invalid.discard(result.slug)
        elif result.status == "not_found":
            invalid.add(result.slug)
            active.discard(result.slug)

    transitions = {
        "activated": sorted(active - previous.active),
        "invalidated": sorted(invalid - previous.invalid),
        "reactivated": sorted((active & previous.invalid)),
        "newly_processed": sorted(processed - previous.processed),
    }
    return SlugState(active=active, invalid=invalid, processed=processed), transitions


async def run_greenhouse_happy_path(
    limit: int,
    target_location: str,
    max_concurrency: int = GREENHOUSE_MAX_CONCURRENCY,
    rate_limit_per_sec: int = GREENHOUSE_RATE_LIMIT_PER_SEC,
) -> dict[str, Any]:
    state_store = _build_state_store()
    all_source_slugs = state_store.load_source_slugs()
    previous_state = state_store.load_state()
    slugs = state_store.select_slugs_for_run(
        all_source_slugs=all_source_slugs,
        state=previous_state,
        limit=limit,
    )
    logger.info(
        "Run config: limit=%s concurrency=%s rate_limit=%s/s source=%s state_dir=%s",
        limit,
        max_concurrency,
        rate_limit_per_sec,
        GREENHOUSE_SLUGS_PATH,
        GREENHOUSE_STATE_DIR,
    )

    funnel = _make_funnel(total_slugs=len(slugs))
    matches: list[dict[str, Any]] = []
    semaphore = asyncio.Semaphore(max_concurrency)
    rate_limiter = AsyncRateLimiter(rate_limit_per_sec)

    async with GreenhouseClient() as client:
        tasks = [
            _process_slug(
                slug=slug,
                target_location=target_location,
                client=client,
                semaphore=semaphore,
                rate_limiter=rate_limiter,
            )
            for slug in slugs
        ]
        results = await asyncio.gather(*tasks)

    for result in results:
        if result.status == "not_found":
            funnel["portal_not_found"] += 1
            continue

        if result.status == "error":
            funnel["portal_error"] += 1
            logger.warning(
                "Portal error slug=%s error=%s",
                result.slug,
                result.error,
            )
            continue

        funnel["portal_active"] += 1
        if result.matched_records:
            funnel["active_with_ai_roles"] += 1
        else:
            funnel["active_without_ai_roles"] += 1

        for match in result.matched_records:
            matches.append(match)
            funnel["ai_roles_total"] += 1
            funnel_key = f"eligible_{match['eligibility']}"
            funnel[funnel_key] += 1

    updated_state, transitions = _apply_state_transitions(previous_state, results)
    run_id = datetime.now(UTC).strftime("run_%Y%m%dT%H%M%S%fZ")
    observed_at_utc = datetime.now(UTC).isoformat()
    master_store = GreenhouseMasterStore(OUTPUT_MASTER_MATCHES_PATH)
    master_upsert = master_store.upsert_many(
        records=matches,
        run_id=run_id,
        observed_at_utc=observed_at_utc,
    )

    run_summary = {
        "run_id": run_id,
        "processed_slugs": slugs,
        "funnel": funnel,
        "state_counts": {
            "active": len(updated_state.active),
            "invalid": len(updated_state.invalid),
            "processed": len(updated_state.processed),
        },
        "state_transitions": transitions,
        "master": {
            "total_records": master_upsert.total_records,
            "inserted_count": master_upsert.inserted_count,
            "updated_count": master_upsert.updated_count,
            "output_path": master_upsert.output_path,
        },
    }
    state_store.save_state(
        all_source_slugs=all_source_slugs,
        state=updated_state,
        run_summary=run_summary,
    )

    OUTPUT_MATCHES_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_MATCHES_PATH.open("w", encoding="utf-8") as file:
        for record in matches:
            file.write(json.dumps(record, ensure_ascii=False) + "\n")

    logger.info("Funnel: %s", json.dumps(funnel, ensure_ascii=False))
    return {
        "funnel": funnel,
        "output_path": str(OUTPUT_MATCHES_PATH),
        "matches_count": len(matches),
        "master_total_records": master_upsert.total_records,
        "master_inserted_count": master_upsert.inserted_count,
        "master_updated_count": master_upsert.updated_count,
        "master_output_path": master_upsert.output_path,
        "state_active_count": len(updated_state.active),
        "state_invalid_count": len(updated_state.invalid),
        "state_processed_count": len(updated_state.processed),
        "state_transitions": transitions,
    }
