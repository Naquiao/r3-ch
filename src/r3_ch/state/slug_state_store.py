"""Derived state store for Greenhouse slug cleanup."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class SlugState:
    active: set[str]
    invalid: set[str]
    processed: set[str]


class GreenhouseSlugStateStore:
    def __init__(
        self,
        source_slugs_path: Path,
        active_slugs_path: Path,
        invalid_slugs_path: Path,
        processed_slugs_path: Path,
        last_run_path: Path,
    ) -> None:
        self._source_slugs_path = source_slugs_path
        self._active_slugs_path = active_slugs_path
        self._invalid_slugs_path = invalid_slugs_path
        self._processed_slugs_path = processed_slugs_path
        self._last_run_path = last_run_path

    def load_source_slugs(self) -> list[str]:
        with self._source_slugs_path.open("r", encoding="utf-8") as file:
            loaded = json.load(file)
        if not isinstance(loaded, list):
            msg = f"Invalid source slug file format: {self._source_slugs_path}"
            raise ValueError(msg)
        return [str(slug) for slug in loaded]

    def load_state(self) -> SlugState:
        active = self._load_slug_set(self._active_slugs_path)
        invalid = self._load_slug_set(self._invalid_slugs_path)
        processed = self._load_slug_set(self._processed_slugs_path)
        # Backward-compatible bootstrap: treat legacy active/invalid as already processed.
        if not self._processed_slugs_path.exists():
            processed = set(active) | set(invalid)
        return SlugState(
            active=active,
            invalid=invalid,
            processed=processed,
        )

    def select_slugs_for_run(self, all_source_slugs: list[str], state: SlugState, limit: int) -> list[str]:
        invalid = state.invalid
        active = state.active
        processed = state.processed

        prioritized_active = [
            slug
            for slug in all_source_slugs
            if slug in active and slug not in invalid and slug not in processed
        ]
        new_candidates = [
            slug
            for slug in all_source_slugs
            if slug not in active and slug not in invalid and slug not in processed
        ]

        selected: list[str] = []
        seen: set[str] = set()
        for slug in prioritized_active + new_candidates:
            if slug in seen:
                continue
            selected.append(slug)
            seen.add(slug)
            if len(selected) >= limit:
                break
        return selected

    def save_state(
        self,
        all_source_slugs: list[str],
        state: SlugState,
        run_summary: dict[str, Any],
    ) -> None:
        self._active_slugs_path.parent.mkdir(parents=True, exist_ok=True)

        source_order = {slug: idx for idx, slug in enumerate(all_source_slugs)}
        active_sorted = sorted(state.active, key=lambda slug: source_order.get(slug, len(source_order)))
        invalid_sorted = sorted(state.invalid, key=lambda slug: source_order.get(slug, len(source_order)))
        processed_sorted = sorted(state.processed, key=lambda slug: source_order.get(slug, len(source_order)))

        with self._active_slugs_path.open("w", encoding="utf-8") as file:
            json.dump(active_sorted, file, ensure_ascii=False, indent=2)
            file.write("\n")

        with self._invalid_slugs_path.open("w", encoding="utf-8") as file:
            json.dump(invalid_sorted, file, ensure_ascii=False, indent=2)
            file.write("\n")

        with self._processed_slugs_path.open("w", encoding="utf-8") as file:
            json.dump(processed_sorted, file, ensure_ascii=False, indent=2)
            file.write("\n")

        payload = {
            "timestamp_utc": datetime.now(UTC).isoformat(),
            **run_summary,
        }
        with self._last_run_path.open("w", encoding="utf-8") as file:
            json.dump(payload, file, ensure_ascii=False, indent=2)
            file.write("\n")

    @staticmethod
    def _load_slug_set(path: Path) -> set[str]:
        if not path.exists():
            return set()
        with path.open("r", encoding="utf-8") as file:
            loaded = json.load(file)
        if not isinstance(loaded, list):
            msg = f"Invalid slug state file format: {path}"
            raise ValueError(msg)
        return {str(slug) for slug in loaded}
