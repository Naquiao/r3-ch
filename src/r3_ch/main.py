"""CLI entrypoint for Greenhouse happy path."""

import argparse
import asyncio
import json
import logging

from r3_ch.config import (
    DEFAULT_SLUG_LIMIT,
    GREENHOUSE_MAX_CONCURRENCY,
    GREENHOUSE_RATE_LIMIT_PER_SEC,
    TARGET_LOCATION,
)
from r3_ch.pipeline.greenhouse_happy_path import run_greenhouse_happy_path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Greenhouse happy path scraper (v1)")
    parser.add_argument(
        "--limit",
        type=int,
        default=DEFAULT_SLUG_LIMIT,
        help=f"Number of Greenhouse slugs to process (default: {DEFAULT_SLUG_LIMIT})",
    )
    parser.add_argument(
        "--target-location",
        default=TARGET_LOCATION,
        help=f"Target location for eligibility checks (default: {TARGET_LOCATION})",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=("DEBUG", "INFO", "WARNING", "ERROR"),
        help="Logging level",
    )
    parser.add_argument(
        "--max-concurrency",
        type=int,
        default=GREENHOUSE_MAX_CONCURRENCY,
        help=f"Maximum in-flight requests (default: {GREENHOUSE_MAX_CONCURRENCY})",
    )
    parser.add_argument(
        "--rate-limit",
        type=int,
        default=GREENHOUSE_RATE_LIMIT_PER_SEC,
        help=f"Maximum requests started per second (default: {GREENHOUSE_RATE_LIMIT_PER_SEC})",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(asctime)s | %(levelname)s | %(message)s",
    )

    result = asyncio.run(
        run_greenhouse_happy_path(
            limit=args.limit,
            target_location=args.target_location,
            max_concurrency=args.max_concurrency,
            rate_limit_per_sec=args.rate_limit,
        )
    )

    print(json.dumps(result["funnel"], indent=2))
    print(f"Run snapshot written to: {result['output_path']}")
    print(
        "Master dataset: "
        f"{result['master_output_path']} "
        f"(total={result['master_total_records']} "
        f"inserted={result['master_inserted_count']} "
        f"updated={result['master_updated_count']})"
    )
    print(
        "State counts: "
        f"active={result['state_active_count']} "
        f"invalid={result['state_invalid_count']} "
        f"processed={result['state_processed_count']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
