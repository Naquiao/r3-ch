"""Application settings for ATS ingestion and matching."""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
GREENHOUSE_SLUGS_PATH = BASE_DIR / "data" / "ats" / "greenhouse_companies.json"
GREENHOUSE_STATE_DIR = BASE_DIR / "data" / "ats" / "state"
GREENHOUSE_ACTIVE_SLUGS_PATH = GREENHOUSE_STATE_DIR / "greenhouse_active_slugs.json"
GREENHOUSE_INVALID_SLUGS_PATH = GREENHOUSE_STATE_DIR / "greenhouse_invalid_slugs.json"
GREENHOUSE_PROCESSED_SLUGS_PATH = GREENHOUSE_STATE_DIR / "greenhouse_processed_slugs.json"
GREENHOUSE_LAST_RUN_PATH = GREENHOUSE_STATE_DIR / "greenhouse_last_run.json"
ASHBY_SLUGS_PATH = BASE_DIR / "data" / "ats" / "ashby_companies.json"
ASHBY_STATE_DIR = BASE_DIR / "data" / "ats" / "state"
ASHBY_ACTIVE_SLUGS_PATH = ASHBY_STATE_DIR / "ashby_active_slugs.json"
ASHBY_INVALID_SLUGS_PATH = ASHBY_STATE_DIR / "ashby_invalid_slugs.json"
ASHBY_PROCESSED_SLUGS_PATH = ASHBY_STATE_DIR / "ashby_processed_slugs.json"
ASHBY_LAST_RUN_PATH = ASHBY_STATE_DIR / "ashby_last_run.json"
LEVER_SLUGS_PATH = BASE_DIR / "data" / "ats" / "lever_companies.json"
LEVER_STATE_DIR = BASE_DIR / "data" / "ats" / "state"
LEVER_ACTIVE_SLUGS_PATH = LEVER_STATE_DIR / "lever_active_slugs.json"
LEVER_INVALID_SLUGS_PATH = LEVER_STATE_DIR / "lever_invalid_slugs.json"
LEVER_PROCESSED_SLUGS_PATH = LEVER_STATE_DIR / "lever_processed_slugs.json"
LEVER_LAST_RUN_PATH = LEVER_STATE_DIR / "lever_last_run.json"
BAMBOOHR_SLUGS_PATH = BASE_DIR / "data" / "ats" / "bamboohr_companies.json"
BAMBOOHR_STATE_DIR = BASE_DIR / "data" / "ats" / "state"
BAMBOOHR_ACTIVE_SLUGS_PATH = BAMBOOHR_STATE_DIR / "bamboohr_active_slugs.json"
BAMBOOHR_INVALID_SLUGS_PATH = BAMBOOHR_STATE_DIR / "bamboohr_invalid_slugs.json"
BAMBOOHR_PROCESSED_SLUGS_PATH = BAMBOOHR_STATE_DIR / "bamboohr_processed_slugs.json"
BAMBOOHR_LAST_RUN_PATH = BAMBOOHR_STATE_DIR / "bamboohr_last_run.json"
OUTPUT_DIR = BASE_DIR / "outputs"
OUTPUT_MATCHES_PATH = OUTPUT_DIR / "greenhouse_matches.jsonl"
OUTPUT_ELIGIBLE_OK_MATCHES_PATH = OUTPUT_DIR / "greenhouse_eligible_ok_matches.json"
OUTPUT_MASTER_MATCHES_PATH = OUTPUT_DIR / "greenhouse_matches_master.json"
OUTPUT_ASHBY_MATCHES_PATH = OUTPUT_DIR / "ashby_matches.jsonl"
OUTPUT_ASHBY_MASTER_MATCHES_PATH = OUTPUT_DIR / "ashby_matches_master.json"
OUTPUT_LEVER_MATCHES_PATH = OUTPUT_DIR / "lever_matches.jsonl"
OUTPUT_LEVER_MASTER_MATCHES_PATH = OUTPUT_DIR / "lever_matches_master.json"
OUTPUT_BAMBOOHR_MATCHES_PATH = OUTPUT_DIR / "bamboohr_matches.jsonl"
OUTPUT_BAMBOOHR_MASTER_MATCHES_PATH = OUTPUT_DIR / "bamboohr_matches_master.json"

DEFAULT_TIMEOUT_SECONDS = 20.0
DEFAULT_SLUG_LIMIT = 10

GREENHOUSE_API_TEMPLATE = "https://boards-api.greenhouse.io/v1/boards/{slug}/jobs?content=true"
GREENHOUSE_MAX_CONCURRENCY = 20
GREENHOUSE_RATE_LIMIT_PER_SEC = 20

ASHBY_API_TEMPLATE = "https://api.ashbyhq.com/posting-api/job-board/{slug}"
ASHBY_MAX_CONCURRENCY = 5
ASHBY_RATE_LIMIT_PER_SEC = 1.0
LEVER_API_TEMPLATE = "https://api.lever.co/v0/postings/{slug}?mode=json"
LEVER_MAX_CONCURRENCY = 10
LEVER_RATE_LIMIT_PER_SEC = 5.0
BAMBOOHR_CAREERS_URL_TEMPLATE = "https://{slug}.bamboohr.com/careers"
BAMBOOHR_MAX_CONCURRENCY = 5
BAMBOOHR_RATE_LIMIT_PER_SEC = 2.0

TARGET_LOCATION = "Cordoba, Argentina"

AI_ROLE_KEYWORDS = (
    "ai engineer",
    "ml engineer",
    "machine learning engineer",
    "llm engineer",
    "artificial intelligence engineer",
    "applied ai engineer",
    "applied machine learning engineer",
)

LATAM_LOCATION_HINTS = (
    "argentina",
    "cordoba",
    "córdoba",
    "latam",
    "latin america",
    "south america",
    "brazil",
    "mexico",
    "chile",
    "colombia",
    "peru",
    "uruguay",
)

REMOTE_OK_HINTS = (
    "remote",
    "remoto",
    "work from home",
    "wfh",
)

REMOTE_SCOPE_HINTS = (
    "latam",
    "latin america",
    "americas",
    "worldwide",
    "global",
    "anywhere",
)
