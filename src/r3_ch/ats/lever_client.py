"""Lever postings API client."""

from dataclasses import dataclass
from typing import Any

import httpx

from r3_ch.config import DEFAULT_TIMEOUT_SECONDS, LEVER_API_TEMPLATE


@dataclass(slots=True)
class LeverFetchResult:
    slug: str
    status: str
    jobs: list[dict[str, Any]]
    error: str | None = None


class LeverClient:
    def __init__(self, timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS) -> None:
        self._client = httpx.AsyncClient(timeout=timeout_seconds)

    async def close(self) -> None:
        await self._client.aclose()

    async def __aenter__(self) -> "LeverClient":
        return self

    async def __aexit__(self, exc_type: object, exc: object, traceback: object) -> None:
        await self.close()

    async def fetch_jobs(self, slug: str) -> LeverFetchResult:
        url = LEVER_API_TEMPLATE.format(slug=slug)
        try:
            response = await self._client.get(url)
        except httpx.HTTPError as exc:
            return LeverFetchResult(slug=slug, status="error", jobs=[], error=str(exc))

        if response.status_code == 404:
            return LeverFetchResult(slug=slug, status="not_found", jobs=[])

        if response.status_code != 200:
            return LeverFetchResult(
                slug=slug,
                status="error",
                jobs=[],
                error=f"unexpected_status_{response.status_code}",
            )

        try:
            payload = response.json()
        except ValueError as exc:
            return LeverFetchResult(
                slug=slug,
                status="error",
                jobs=[],
                error=f"invalid_json: {exc}",
            )

        jobs: list[dict[str, Any]]
        if isinstance(payload, list):
            jobs = [entry for entry in payload if isinstance(entry, dict)]
        elif isinstance(payload, dict):
            raw_jobs = payload.get("data")
            if isinstance(raw_jobs, list):
                jobs = [entry for entry in raw_jobs if isinstance(entry, dict)]
            else:
                return LeverFetchResult(
                    slug=slug,
                    status="error",
                    jobs=[],
                    error="invalid_jobs_schema",
                )
        else:
            return LeverFetchResult(
                slug=slug,
                status="error",
                jobs=[],
                error="invalid_jobs_schema",
            )

        return LeverFetchResult(slug=slug, status="active", jobs=jobs)
