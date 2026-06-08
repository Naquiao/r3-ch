# r3-ch

Happy path v1 for scraping AI/ML/LLM roles from Greenhouse company boards.

## Setup (uv)

```bash
uv sync
```

## Run Greenhouse happy path

Default run:

```bash
uv run r3-ch
```

Useful flags:

```bash
uv run r3-ch --limit 10 --target-location "Cordoba, Argentina" --max-concurrency 20 --rate-limit 20 --log-level INFO
```

## What it does in v1

- Reads the first N slugs from `data/ats/greenhouse_companies.json`
- Calls `https://boards-api.greenhouse.io/v1/boards/{slug}/jobs?content=true`
- Runs requests concurrently with:
  - max in-flight requests: `--max-concurrency` (default `20`)
  - max request starts/second: `--rate-limit` (default `20`)
- Filters jobs by initial AI role keywords:
  - `ai engineer`
  - `ml engineer`
  - `machine learning engineer`
  - `llm engineer`
- Evaluates eligibility for Cordoba, Argentina using `ok | not_eligible | unknown`
- Logs funnel counts:
  - `total_slugs_considered`
  - `portal_active`
  - `portal_not_found`
  - `portal_error`
  - `active_with_ai_roles`
  - `active_without_ai_roles`
  - `ai_roles_total`
  - `eligible_ok`
  - `eligible_not_eligible`
  - `eligible_unknown`

## Outputs

- Run snapshot (debug/current batch): `outputs/greenhouse_matches.jsonl`
- Master accumulated dataset (for UI): `outputs/greenhouse_matches_master.json`
  - one record per `slug + job_id` (upsert, no duplication by reruns)
  - fields: `slug`, `job_id`, `title`, `updated_at`, `location_raw`, `eligibility`, `absolute_url`, `matched_keywords`, `target_location`, `first_seen_at`, `last_seen_at`, `last_run_id`

## Derived slug cleanup state

Source slugs are kept immutable in:

- `data/ats/greenhouse_companies.json`

Cleanup state is written to:

- `data/ats/state/greenhouse_active_slugs.json`
- `data/ats/state/greenhouse_invalid_slugs.json`
- `data/ats/state/greenhouse_processed_slugs.json`
- `data/ats/state/greenhouse_last_run.json`

Current policy:

- any attempted slug (`active`, `not_found`, `error`) is marked as processed and skipped in future runs
- `404` in a run => slug is marked invalid immediately (`1x404`).
- `200` in a later run => slug is re-activated automatically.
- network/runtime `error` => slug state is not changed.

## Master upsert semantics

- Dedup key: `slug + job_id`
- First observation: create record and set `first_seen_at` / `last_seen_at`
- Subsequent observation of same key: update mutable fields (`title`, `updated_at`, `location_raw`, `eligibility`, `absolute_url`, `matched_keywords`, `target_location`) and refresh `last_seen_at` / `last_run_id`
- Records are not auto-deleted from master in this iteration