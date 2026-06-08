"""AI role keyword matching."""

import re

from r3_ch.config import AI_ROLE_KEYWORDS


def _normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", value.lower()).strip()


def _keyword_hits(text: str) -> list[str]:
    hits: list[str] = []
    for keyword in AI_ROLE_KEYWORDS:
        pattern = rf"\b{re.escape(keyword)}\b"
        if re.search(pattern, text):
            hits.append(keyword)
    return hits


def match_ai_role_keywords(title: str | None, content: str | None) -> list[str]:
    normalized_title = _normalize_text(title or "")
    return _keyword_hits(normalized_title)

