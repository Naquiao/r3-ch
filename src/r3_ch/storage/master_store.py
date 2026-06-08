"""Master dataset store with upsert semantics for UI consumption."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any


@dataclass(slots=True)
class MasterUpsertResult:
    total_records: int
    inserted_count: int
    updated_count: int
    output_path: str


class GreenhouseMasterStore:
    def __init__(self, master_path: Path) -> None:
        self._master_path = master_path

    def upsert_many(
        self,
        records: list[dict[str, Any]],
        run_id: str,
        observed_at_utc: str,
    ) -> MasterUpsertResult:
        master_records = self._load_master()
        indexed = {self._record_key(record): record for record in master_records}

        inserted_count = 0
        updated_count = 0

        for record in records:
            key = self._record_key(record)
            existing = indexed.get(key)
            if existing is None:
                indexed[key] = {
                    **record,
                    "first_seen_at": observed_at_utc,
                    "last_seen_at": observed_at_utc,
                    "last_run_id": run_id,
                }
                inserted_count += 1
                continue

            existing.update(
                {
                    "title": record.get("title"),
                    "updated_at": record.get("updated_at"),
                    "location_raw": record.get("location_raw"),
                    "eligibility": record.get("eligibility"),
                    "absolute_url": record.get("absolute_url"),
                    "matched_keywords": record.get("matched_keywords"),
                    "target_location": record.get("target_location"),
                    "last_seen_at": observed_at_utc,
                    "last_run_id": run_id,
                }
            )
            updated_count += 1

        ordered_records = sorted(
            indexed.values(),
            key=lambda item: (str(item.get("slug", "")), str(item.get("job_id", ""))),
        )
        self._write_master(ordered_records)
        return MasterUpsertResult(
            total_records=len(ordered_records),
            inserted_count=inserted_count,
            updated_count=updated_count,
            output_path=str(self._master_path),
        )

    def _load_master(self) -> list[dict[str, Any]]:
        if not self._master_path.exists():
            return []
        with self._master_path.open("r", encoding="utf-8") as file:
            loaded = json.load(file)
        if not isinstance(loaded, list):
            msg = f"Invalid master file format: {self._master_path}"
            raise ValueError(msg)
        return [entry for entry in loaded if isinstance(entry, dict)]

    def _write_master(self, records: list[dict[str, Any]]) -> None:
        self._master_path.parent.mkdir(parents=True, exist_ok=True)
        with NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=self._master_path.parent,
            delete=False,
            suffix=".tmp",
        ) as tmp:
            json.dump(records, tmp, ensure_ascii=False, indent=2)
            tmp.write("\n")
            tmp_path = Path(tmp.name)
        tmp_path.replace(self._master_path)

    @staticmethod
    def _record_key(record: dict[str, Any]) -> str:
        return f"{record.get('slug')}:{record.get('job_id')}"
