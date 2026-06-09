# r3-ch

Happy path for scraping AI/ML/LLM roles from multiple ATS providers (Greenhouse + Ashby + Lever + BambooHR).

## Setup (uv)

```bash
uv sync
```

## Run ATS ingestion

Default run (Greenhouse only):

```bash
uv run r3-ch
```

Useful flags:

```bash
uv run r3-ch --ats all --limit 10 --target-location "Cordoba, Argentina" --greenhouse-max-concurrency 20 --greenhouse-rate-limit 20 --ashby-max-concurrency 5 --ashby-rate-limit 1.0 --lever-max-concurrency 10 --lever-rate-limit 5.0 --bamboohr-max-concurrency 5 --bamboohr-rate-limit 2.0 --log-level INFO
```

## What it does

- Supports provider selection via `--ats greenhouse|ashby|lever|bamboohr|all`.
- Reads slugs from:
  - `data/ats/greenhouse_companies.json`
  - `data/ats/ashby_companies.json`
  - `data/ats/lever_companies.json`
  - `data/ats/bamboohr_companies.json`
- Calls:
  - Greenhouse: `https://boards-api.greenhouse.io/v1/boards/{slug}/jobs?content=true`
  - Ashby: `https://api.ashbyhq.com/posting-api/job-board/{slug}`
  - Lever: `https://api.lever.co/v0/postings/{slug}?mode=json`
  - BambooHR: `https://{slug}.bamboohr.com/careers` (public scraping fallbacks)
- Runs requests concurrently with provider-specific limits:
  - Greenhouse defaults: max in-flight `20`, max starts/s `20`
  - Ashby defaults: max in-flight `5`, max starts/s `1.0`
  - Lever defaults: max in-flight `10`, max starts/s `5.0`
  - BambooHR defaults: max in-flight `5`, max starts/s `2.0`
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

## Outputs (separate per ATS)

- Greenhouse run snapshot: `outputs/greenhouse_matches.jsonl`
- Greenhouse master: `outputs/greenhouse_matches_master.json`
- Ashby run snapshot: `outputs/ashby_matches.jsonl`
- Ashby master: `outputs/ashby_matches_master.json`
- Lever run snapshot: `outputs/lever_matches.jsonl`
- Lever master: `outputs/lever_matches_master.json`
- BambooHR run snapshot: `outputs/bamboohr_matches.jsonl`
- BambooHR master: `outputs/bamboohr_matches_master.json`
- Master records use one record per `slug + job_id` within each ATS file (upsert, no duplication by reruns)
- Shared record shape: `ats`, `slug`, `job_id`, `title`, `updated_at`, `location_raw`, `eligibility`, `absolute_url`, `matched_keywords`, `target_location`, `first_seen_at`, `last_seen_at`, `last_run_id`, `description`
  - *Nota sobre descripciones*: Para roles elegibles (`eligibility = ok`), el pipeline de ingesta intenta guardar siempre una `description` válida. Si el campo principal del payload (p.ej. `content`) viene vacío, se utilizan fallbacks del payload (como `descriptionPlain` o `description`).

## Derived slug cleanup state

Source slugs are kept immutable in:

- `data/ats/greenhouse_companies.json`

Cleanup state is written to:

- `data/ats/state/greenhouse_active_slugs.json`
- `data/ats/state/greenhouse_invalid_slugs.json`
- `data/ats/state/greenhouse_processed_slugs.json`
- `data/ats/state/greenhouse_last_run.json`
- `data/ats/state/ashby_active_slugs.json`
- `data/ats/state/ashby_invalid_slugs.json`
- `data/ats/state/ashby_processed_slugs.json`
- `data/ats/state/ashby_last_run.json`
- `data/ats/state/lever_active_slugs.json`
- `data/ats/state/lever_invalid_slugs.json`
- `data/ats/state/lever_processed_slugs.json`
- `data/ats/state/lever_last_run.json`
- `data/ats/state/bamboohr_active_slugs.json`
- `data/ats/state/bamboohr_invalid_slugs.json`
- `data/ats/state/bamboohr_processed_slugs.json`
- `data/ats/state/bamboohr_last_run.json`

Current policy:

- any attempted slug (`active`, `not_found`, `error`) is marked as processed and skipped in future runs
- `404` in a run => slug is marked invalid immediately (`1x404`).
- `200` in a later run => slug is re-activated automatically.
- network/runtime `error` => slug state is not changed.

## Master upsert semantics

- Dedup key (within each ATS master file): `slug + job_id`
- First observation: create record and set `first_seen_at` / `last_seen_at`
- Subsequent observation of same key: update mutable fields (`title`, `updated_at`, `location_raw`, `eligibility`, `absolute_url`, `matched_keywords`, `target_location`) and refresh `last_seen_at` / `last_run_id`
- Records are not auto-deleted from master in this iteration

## Opportunity Review UI (Next.js)

UI app lives in `web/` and reads:

- master opportunities: `outputs/greenhouse_matches_master.json` + `outputs/ashby_matches_master.json` + `outputs/lever_matches_master.json` + `outputs/bamboohr_matches_master.json`
- user decisions: `data/ui/opportunity_evaluations.json`

### Start UI

```bash
npm --prefix web install
npm --prefix web run dev
```

Then open `http://localhost:3000`.

### UI capabilities (Stage 2)

- Lists only eligible opportunities (`eligibility = ok`)
- Filters by location, decision, and ATS (`greenhouse` / `ashby` / `lever` / `bamboohr`)
- Sorts opportunities by Greenhouse `updated_at` datetime (`Newest first` / `Oldest first`, default `Newest first`)
- Shows ATS provenance on each opportunity card
- Decision categories:
  - `Me interesa` (`interested`)
  - `Paso` (`not_interested`)
  - `Later` (`later`)
- Saves decisions via API to `data/ui/opportunity_evaluations.json`
  - key format: `ats:slug:job_id` (legacy `slug:job_id` is still read for compatibility)
- JD description fetch on-demand from `absolute_url` cuando falta en el JSON master.
  - Al fetchear desde la UI, la descripción scrapeada **se persiste automáticamente** en el respectivo master JSON (Greenhouse/Ashby/Lever/BambooHR). Esto hace que futuras recargas de la UI o inspecciones muestren la descripción sin tener que volver a fetchear la URL, aplicando como backfill de aquellos roles que no capturaron descripción durante la ingesta.
  - Política de actualización: la persistencia on-demand solo inserta el dato si el JSON maestro lo tenía vacío, no pisa descripciones existentes para no perder el original.