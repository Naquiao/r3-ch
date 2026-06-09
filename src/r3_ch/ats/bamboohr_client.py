"""BambooHR public careers client."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any

import httpx

from r3_ch.config import BAMBOOHR_CAREERS_URL_TEMPLATE, DEFAULT_TIMEOUT_SECONDS


@dataclass(slots=True)
class BambooHrFetchResult:
    slug: str
    status: str
    jobs: list[dict[str, Any]]
    error: str | None = None


class BambooHrClient:
    def __init__(self, timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS) -> None:
        self._client = httpx.AsyncClient(timeout=timeout_seconds)

    async def close(self) -> None:
        await self._client.aclose()

    async def __aenter__(self) -> "BambooHrClient":
        return self

    async def __aexit__(self, exc_type: object, exc: object, traceback: object) -> None:
        await self.close()

    async def fetch_jobs(self, slug: str) -> BambooHrFetchResult:
        url = BAMBOOHR_CAREERS_URL_TEMPLATE.format(slug=slug)
        try:
            response = await self._client.get(url)
        except httpx.HTTPError as exc:
            return BambooHrFetchResult(
                slug=slug,
                status="error",
                jobs=[],
                error=str(exc),
            )

        if response.status_code == 404:
            return BambooHrFetchResult(slug=slug, status="not_found", jobs=[])

        if response.status_code != 200:
            return BambooHrFetchResult(
                slug=slug,
                status="error",
                jobs=[],
                error=f"unexpected_status_{response.status_code}",
            )

        body = response.text
        jobs: list[dict[str, Any]] = []

        parsed_json: Any | None = None
        try:
            parsed_json = response.json()
        except ValueError:
            parsed_json = None

        if parsed_json is not None:
            jobs = _extract_jobs_from_json_payload(parsed_json)

        if not jobs:
            jobs = _extract_jobs_from_html(body)

        return BambooHrFetchResult(slug=slug, status="active", jobs=jobs)


def _extract_jobs_from_json_payload(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return [entry for entry in payload if isinstance(entry, dict)]

    if not isinstance(payload, dict):
        return []

    for key in ("jobs", "jobOpenings", "openings", "results", "data"):
        value = payload.get(key)
        if isinstance(value, list):
            return [entry for entry in value if isinstance(entry, dict)]

    return []


def _extract_jobs_from_html(html: str) -> list[dict[str, Any]]:
    jobs: list[dict[str, Any]] = []

    json_ld_blocks = re.findall(
        r"<script[^>]*type=[\"']application/ld\+json[\"'][^>]*>(.*?)</script>",
        html,
        flags=re.IGNORECASE | re.DOTALL,
    )
    for block in json_ld_blocks:
        try:
            payload = json.loads(block.strip())
        except ValueError:
            continue

        for entry in _iter_json_ld_entries(payload):
            if not isinstance(entry, dict):
                continue
            if entry.get("@type") != "JobPosting":
                continue
            title = entry.get("title")
            url = entry.get("url")
            if not isinstance(title, str) or not title.strip():
                continue
            jobs.append(
                {
                    "id": entry.get("identifier") or url or title,
                    "title": title.strip(),
                    "text": title.strip(),
                    "description": entry.get("description"),
                    "url": url,
                    "updatedAt": entry.get("datePosted"),
                    "location": _extract_json_ld_location(entry),
                }
            )

    if jobs:
        return jobs

    # Fallback: detect visible links to job detail pages.
    for match in re.finditer(
        r'<a[^>]+href=[\"\'](?P<href>[^\"\']+/careers/[^\"\']+)[\"\'][^>]*>(?P<label>.*?)</a>',
        html,
        flags=re.IGNORECASE | re.DOTALL,
    ):
        href = match.group("href").strip()
        label = _strip_html(match.group("label"))
        if not label:
            continue
        jobs.append(
            {
                "id": href.rstrip("/").rsplit("/", 1)[-1],
                "title": label,
                "text": label,
                "url": href,
            }
        )

    return jobs


def _iter_json_ld_entries(payload: Any) -> list[Any]:
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        graph = payload.get("@graph")
        if isinstance(graph, list):
            return graph
        return [payload]
    return []


def _extract_json_ld_location(entry: dict[str, Any]) -> str | None:
    location = entry.get("jobLocation")
    if isinstance(location, list) and location:
        location = location[0]
    if isinstance(location, dict):
        address = location.get("address")
        if isinstance(address, dict):
            city = address.get("addressLocality")
            country = address.get("addressCountry")
            parts = [part.strip() for part in (city, country) if isinstance(part, str) and part.strip()]
            if parts:
                return ", ".join(parts)
        name = location.get("name")
        if isinstance(name, str) and name.strip():
            return name.strip()
    return None


def _strip_html(value: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", value)).strip()
