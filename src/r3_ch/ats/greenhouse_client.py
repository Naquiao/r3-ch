"""Greenhouse API client."""

from dataclasses import dataclass
from typing import Any

import httpx

from r3_ch.config import DEFAULT_TIMEOUT_SECONDS, GREENHOUSE_API_TEMPLATE


@dataclass(slots=True)
class GreenhouseFetchResult:
    slug: str
    status: str
    jobs: list[dict[str, Any]]
    error: str | None = None


class GreenhouseClient:
    def __init__(self, timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS) -> None:
        self._client = httpx.AsyncClient(timeout=timeout_seconds)

    async def close(self) -> None:
        await self._client.aclose()

    async def __aenter__(self) -> "GreenhouseClient":
        return self

    async def __aexit__(self, exc_type: object, exc: object, traceback: object) -> None:
        await self.close()

    async def fetch_jobs(self, slug: str) -> GreenhouseFetchResult:
        url = GREENHOUSE_API_TEMPLATE.format(slug=slug)
        try:
            response = await self._client.get(url)
        except httpx.HTTPError as exc:
            return GreenhouseFetchResult(
                slug=slug,
                status="error",
                jobs=[],
                error=str(exc),
            )

        if response.status_code == 404:
            return GreenhouseFetchResult(
                slug=slug,
                status="not_found",
                jobs=[],
            )

        if response.status_code != 200:
            return GreenhouseFetchResult(
                slug=slug,
                status="error",
                jobs=[],
                error=f"unexpected_status_{response.status_code}",
            )

        try:
            payload = response.json()
        except ValueError as exc:
            return GreenhouseFetchResult(
                slug=slug,
                status="error",
                jobs=[],
                error=f"invalid_json: {exc}",
            )

        jobs = payload.get("jobs", [])
        if not isinstance(jobs, list):
            return GreenhouseFetchResult(
                slug=slug,
                status="error",
                jobs=[],
                error="invalid_jobs_schema",
            )

        return GreenhouseFetchResult(
            slug=slug,
            status="active",
            jobs=jobs,
        )
