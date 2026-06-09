"""Ashby public job board API client."""

from dataclasses import dataclass
from typing import Any

import httpx

from r3_ch.config import ASHBY_API_TEMPLATE, DEFAULT_TIMEOUT_SECONDS


@dataclass(slots=True)
class AshbyFetchResult:
    slug: str
    status: str
    jobs: list[dict[str, Any]]
    error: str | None = None


class AshbyClient:
    def __init__(self, timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS) -> None:
        self._client = httpx.AsyncClient(timeout=timeout_seconds)

    async def close(self) -> None:
        await self._client.aclose()

    async def __aenter__(self) -> "AshbyClient":
        return self

    async def __aexit__(self, exc_type: object, exc: object, traceback: object) -> None:
        await self.close()

    async def fetch_jobs(self, slug: str) -> AshbyFetchResult:
        url = ASHBY_API_TEMPLATE.format(slug=slug)
        try:
            response = await self._client.get(url)
        except httpx.HTTPError as exc:
            return AshbyFetchResult(
                slug=slug,
                status="error",
                jobs=[],
                error=str(exc),
            )

        if response.status_code == 404:
            return AshbyFetchResult(
                slug=slug,
                status="not_found",
                jobs=[],
            )

        if response.status_code != 200:
            return AshbyFetchResult(
                slug=slug,
                status="error",
                jobs=[],
                error=f"unexpected_status_{response.status_code}",
            )

        try:
            payload = response.json()
        except ValueError as exc:
            return AshbyFetchResult(
                slug=slug,
                status="error",
                jobs=[],
                error=f"invalid_json: {exc}",
            )

        jobs = payload.get("jobs", [])
        if not isinstance(jobs, list):
            return AshbyFetchResult(
                slug=slug,
                status="error",
                jobs=[],
                error="invalid_jobs_schema",
            )

        normalized_jobs = [job for job in jobs if isinstance(job, dict)]
        return AshbyFetchResult(
            slug=slug,
            status="active",
            jobs=normalized_jobs,
        )
