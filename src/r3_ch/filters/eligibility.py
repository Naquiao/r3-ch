"""Eligibility rules for target location."""

import re

from r3_ch.config import LATAM_LOCATION_HINTS, REMOTE_OK_HINTS, REMOTE_SCOPE_HINTS

EligibilityStatus = str


def _normalize(value: str) -> str:
    return re.sub(r"\s+", " ", value.lower()).strip()


def evaluate_eligibility(location_raw: str | None) -> EligibilityStatus:
    if not location_raw:
        return "unknown"

    text = _normalize(location_raw)

    if any(hint in text for hint in LATAM_LOCATION_HINTS):
        return "ok"

    has_remote = any(hint in text for hint in REMOTE_OK_HINTS)
    has_wide_scope = any(hint in text for hint in REMOTE_SCOPE_HINTS)
    if has_remote and has_wide_scope:
        return "ok"

    # Explicit location but no matching LATAM/remote-global hints.
    if text:
        return "not_eligible"

    return "unknown"
