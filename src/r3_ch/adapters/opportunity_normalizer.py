"""Normalize ATS payloads into the shared opportunity record shape."""

from __future__ import annotations

from hashlib import sha1
from typing import Any

ATS_GREENHOUSE = "greenhouse"
ATS_ASHBY = "ashby"
ATS_LEVER = "lever"
ATS_BAMBOOHR = "bamboohr"


def normalize_greenhouse_job(
    *,
    slug: str,
    job: dict[str, Any],
    target_location: str,
    matched_keywords: list[str],
    eligibility: str,
) -> dict[str, Any]:
    description = job.get("content")
    if eligibility == "ok" and not description:
        description = job.get("description") or job.get("descriptionPlain") or job.get("descriptionHtml")
        
    return {
        "ats": ATS_GREENHOUSE,
        "slug": slug,
        "job_id": job.get("id"),
        "title": str(job.get("title", "")),
        "updated_at": job.get("updated_at"),
        "location_raw": _extract_greenhouse_location_name(job),
        "eligibility": eligibility,
        "absolute_url": job.get("absolute_url"),
        "matched_keywords": matched_keywords,
        "target_location": target_location,
        "description": description,
    }


def normalize_ashby_job(
    *,
    slug: str,
    job: dict[str, Any],
    target_location: str,
    matched_keywords: list[str],
    eligibility: str,
) -> dict[str, Any]:
    absolute_url = _extract_ashby_absolute_url(job)
    job_id = _extract_ashby_job_id(job, absolute_url)
    location_raw = extract_ashby_location(job)
    
    description = job.get("descriptionPlain") or job.get("descriptionHtml")
    if eligibility == "ok" and not description:
        description = job.get("content") or job.get("description")
        
    return {
        "ats": ATS_ASHBY,
        "slug": slug,
        "job_id": job_id,
        "title": str(job.get("title", "")),
        "updated_at": job.get("publishedAt") or job.get("updatedAt"),
        "location_raw": location_raw,
        "eligibility": eligibility,
        "absolute_url": absolute_url,
        "matched_keywords": matched_keywords,
        "target_location": target_location,
        "description": description,
    }


def normalize_lever_job(
    *,
    slug: str,
    job: dict[str, Any],
    target_location: str,
    matched_keywords: list[str],
    eligibility: str,
) -> dict[str, Any]:
    absolute_url = _extract_lever_absolute_url(job)
    job_id = _extract_lever_job_id(job, absolute_url)
    location_raw = extract_lever_location(job)

    description = (
        job.get("descriptionPlain")
        or job.get("description")
        or job.get("descriptionHtml")
        or job.get("content")
        or job.get("text")
    )
    if eligibility == "ok" and not description:
        lists = job.get("lists")
        if isinstance(lists, list):
            description = _extract_text_from_lists(lists)

    return {
        "ats": ATS_LEVER,
        "slug": slug,
        "job_id": job_id,
        "title": str(job.get("text", "") or job.get("title", "")),
        "updated_at": job.get("updatedAt") or job.get("createdAt"),
        "location_raw": location_raw,
        "eligibility": eligibility,
        "absolute_url": absolute_url,
        "matched_keywords": matched_keywords,
        "target_location": target_location,
        "description": description,
    }


def normalize_bamboohr_job(
    *,
    slug: str,
    job: dict[str, Any],
    target_location: str,
    matched_keywords: list[str],
    eligibility: str,
) -> dict[str, Any]:
    absolute_url = _extract_bamboohr_absolute_url(job)
    job_id = _extract_bamboohr_job_id(job, absolute_url)
    location_raw = extract_bamboohr_location(job)

    description = (
        job.get("descriptionPlain")
        or job.get("description")
        or job.get("content")
        or job.get("descriptionHtml")
    )
    if eligibility == "ok" and not description:
        description = job.get("text")

    return {
        "ats": ATS_BAMBOOHR,
        "slug": slug,
        "job_id": job_id,
        "title": str(job.get("text", "") or job.get("title", "")),
        "updated_at": job.get("updatedAt") or job.get("createdAt") or job.get("datePosted"),
        "location_raw": location_raw,
        "eligibility": eligibility,
        "absolute_url": absolute_url,
        "matched_keywords": matched_keywords,
        "target_location": target_location,
        "description": description,
    }


def _extract_greenhouse_location_name(job: dict[str, Any]) -> str | None:
    location = job.get("location")
    if isinstance(location, dict):
        value = location.get("name")
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None


def _extract_ashby_absolute_url(job: dict[str, Any]) -> str | None:
    for key in ("jobUrl", "absolute_url", "url", "jobPostUrl"):
        value = job.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None


def _extract_ashby_job_id(job: dict[str, Any], absolute_url: str | None) -> str:
    for key in ("id", "jobId", "_id", "externalId"):
        value = job.get(key)
        if value is None:
            continue
        text = str(value).strip()
        if text:
            return text

    if absolute_url:
        tail = absolute_url.rstrip("/").rsplit("/", 1)[-1].strip()
        if tail:
            return tail

    # Stable fallback for unexpected payloads.
    payload_hash = sha1(str(sorted(job.items())).encode("utf-8"), usedforsecurity=False).hexdigest()
    return payload_hash


def _extract_lever_absolute_url(job: dict[str, Any]) -> str | None:
    for key in ("hostedUrl", "absolute_url", "url", "applyUrl"):
        value = job.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None


def _extract_bamboohr_absolute_url(job: dict[str, Any]) -> str | None:
    for key in ("url", "hostedUrl", "absolute_url", "jobUrl"):
        value = job.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None


def _extract_lever_job_id(job: dict[str, Any], absolute_url: str | None) -> str:
    for key in ("id", "_id", "jobId", "externalId"):
        value = job.get(key)
        if value is None:
            continue
        text = str(value).strip()
        if text:
            return text

    if absolute_url:
        tail = absolute_url.rstrip("/").rsplit("/", 1)[-1].strip()
        if tail:
            return tail

    payload_hash = sha1(str(sorted(job.items())).encode("utf-8"), usedforsecurity=False).hexdigest()
    return payload_hash


def _extract_bamboohr_job_id(job: dict[str, Any], absolute_url: str | None) -> str:
    for key in ("id", "jobId", "requisitionId", "_id"):
        value = job.get(key)
        if value is None:
            continue
        text = str(value).strip()
        if text:
            return text

    if absolute_url:
        tail = absolute_url.rstrip("/").rsplit("/", 1)[-1].strip()
        if tail:
            return tail

    payload_hash = sha1(str(sorted(job.items())).encode("utf-8"), usedforsecurity=False).hexdigest()
    return payload_hash


def _extract_text_from_lists(lists: list[Any]) -> str | None:
    for entry in lists:
        if not isinstance(entry, dict):
            continue
        content = entry.get("content")
        if isinstance(content, str) and content.strip():
            return content.strip()
        text = entry.get("text")
        if isinstance(text, str) and text.strip():
            return text.strip()
    return None


def extract_ashby_location(job: dict[str, Any]) -> str | None:
    parts: list[str] = []

    primary = job.get("location")
    if isinstance(primary, str) and primary.strip():
        parts.append(primary.strip())

    secondary = job.get("secondaryLocations")
    if isinstance(secondary, list):
        for entry in secondary:
            if not isinstance(entry, dict):
                continue
            location = entry.get("location")
            if isinstance(location, str) and location.strip():
                parts.append(location.strip())

    workplace_type = job.get("workplaceType")
    if isinstance(workplace_type, str) and workplace_type.strip():
        parts.append(workplace_type.strip())

    is_remote = job.get("isRemote")
    if is_remote is True:
        parts.append("remote")

    address = job.get("address")
    if isinstance(address, dict):
        postal = address.get("postalAddress")
        if isinstance(postal, dict):
            country = postal.get("addressCountry")
            if isinstance(country, str) and country.strip():
                parts.append(country.strip())

    if not parts:
        return None
    return ", ".join(dict.fromkeys(parts))


def extract_lever_location(job: dict[str, Any]) -> str | None:
    parts: list[str] = []
    categories = job.get("categories")
    if isinstance(categories, dict):
        for key in ("location", "team", "commitment", "allLocations"):
            value = categories.get(key)
            if isinstance(value, str) and value.strip():
                parts.append(value.strip())

    workplace_type = job.get("workplaceType")
    if isinstance(workplace_type, str) and workplace_type.strip():
        parts.append(workplace_type.strip())

    if not parts:
        return None
    return ", ".join(dict.fromkeys(parts))


def extract_bamboohr_location(job: dict[str, Any]) -> str | None:
    parts: list[str] = []
    for key in ("location", "city", "country", "employmentType"):
        value = job.get(key)
        if isinstance(value, str) and value.strip():
            parts.append(value.strip())

    categories = job.get("categories")
    if isinstance(categories, dict):
        for key in ("location", "department"):
            value = categories.get(key)
            if isinstance(value, str) and value.strip():
                parts.append(value.strip())

    if not parts:
        return None
    return ", ".join(dict.fromkeys(parts))
