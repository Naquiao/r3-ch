"""Application settings for the Greenhouse happy path."""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
GREENHOUSE_SLUGS_PATH = BASE_DIR / "data" / "ats" / "greenhouse_companies.json"
GREENHOUSE_STATE_DIR = BASE_DIR / "data" / "ats" / "state"
GREENHOUSE_ACTIVE_SLUGS_PATH = GREENHOUSE_STATE_DIR / "greenhouse_active_slugs.json"
GREENHOUSE_INVALID_SLUGS_PATH = GREENHOUSE_STATE_DIR / "greenhouse_invalid_slugs.json"
GREENHOUSE_PROCESSED_SLUGS_PATH = GREENHOUSE_STATE_DIR / "greenhouse_processed_slugs.json"
GREENHOUSE_LAST_RUN_PATH = GREENHOUSE_STATE_DIR / "greenhouse_last_run.json"
OUTPUT_DIR = BASE_DIR / "outputs"
OUTPUT_MATCHES_PATH = OUTPUT_DIR / "greenhouse_matches.jsonl"
OUTPUT_ELIGIBLE_OK_MATCHES_PATH = OUTPUT_DIR / "greenhouse_eligible_ok_matches.json"
OUTPUT_MASTER_MATCHES_PATH = OUTPUT_DIR / "greenhouse_matches_master.json"

GREENHOUSE_API_TEMPLATE = "https://boards-api.greenhouse.io/v1/boards/{slug}/jobs?content=true"
DEFAULT_TIMEOUT_SECONDS = 20.0
DEFAULT_SLUG_LIMIT = 10
GREENHOUSE_MAX_CONCURRENCY = 20
GREENHOUSE_RATE_LIMIT_PER_SEC = 20

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
