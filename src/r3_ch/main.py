"""CLI entrypoint for ATS ingestion pipelines."""

import argparse
import asyncio
import json
import logging

from r3_ch.config import (
    BAMBOOHR_MAX_CONCURRENCY,
    BAMBOOHR_RATE_LIMIT_PER_SEC,
    ASHBY_MAX_CONCURRENCY,
    ASHBY_RATE_LIMIT_PER_SEC,
    DEFAULT_SLUG_LIMIT,
    GREENHOUSE_MAX_CONCURRENCY,
    GREENHOUSE_RATE_LIMIT_PER_SEC,
    LEVER_MAX_CONCURRENCY,
    LEVER_RATE_LIMIT_PER_SEC,
    TARGET_LOCATION,
)
from r3_ch.pipeline.ashby_happy_path import run_ashby_happy_path
from r3_ch.pipeline.bamboohr_happy_path import run_bamboohr_happy_path
from r3_ch.pipeline.greenhouse_happy_path import run_greenhouse_happy_path
from r3_ch.pipeline.lever_happy_path import run_lever_happy_path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="ATS job ingestion runner (Greenhouse + Ashby + Lever + BambooHR)")
    parser.add_argument(
        "--ats",
        default="greenhouse",
        choices=("greenhouse", "ashby", "lever", "bamboohr", "all"),
        help="ATS provider selector (default: greenhouse)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=DEFAULT_SLUG_LIMIT,
        help=f"Number of slugs to process for each selected ATS (default: {DEFAULT_SLUG_LIMIT})",
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
        "--greenhouse-max-concurrency",
        type=int,
        default=GREENHOUSE_MAX_CONCURRENCY,
        help=f"Greenhouse max in-flight requests (default: {GREENHOUSE_MAX_CONCURRENCY})",
    )
    parser.add_argument(
        "--greenhouse-rate-limit",
        type=float,
        default=GREENHOUSE_RATE_LIMIT_PER_SEC,
        help=f"Greenhouse max requests started per second (default: {GREENHOUSE_RATE_LIMIT_PER_SEC})",
    )
    parser.add_argument(
        "--ashby-max-concurrency",
        type=int,
        default=ASHBY_MAX_CONCURRENCY,
        help=f"Ashby max in-flight requests (default: {ASHBY_MAX_CONCURRENCY})",
    )
    parser.add_argument(
        "--ashby-rate-limit",
        type=float,
        default=ASHBY_RATE_LIMIT_PER_SEC,
        help=f"Ashby max requests started per second (default: {ASHBY_RATE_LIMIT_PER_SEC})",
    )
    parser.add_argument(
        "--lever-max-concurrency",
        type=int,
        default=LEVER_MAX_CONCURRENCY,
        help=f"Lever max in-flight requests (default: {LEVER_MAX_CONCURRENCY})",
    )
    parser.add_argument(
        "--lever-rate-limit",
        type=float,
        default=LEVER_RATE_LIMIT_PER_SEC,
        help=f"Lever max requests started per second (default: {LEVER_RATE_LIMIT_PER_SEC})",
    )
    parser.add_argument(
        "--bamboohr-max-concurrency",
        type=int,
        default=BAMBOOHR_MAX_CONCURRENCY,
        help=f"BambooHR max in-flight requests (default: {BAMBOOHR_MAX_CONCURRENCY})",
    )
    parser.add_argument(
        "--bamboohr-rate-limit",
        type=float,
        default=BAMBOOHR_RATE_LIMIT_PER_SEC,
        help=f"BambooHR max requests started per second (default: {BAMBOOHR_RATE_LIMIT_PER_SEC})",
    )
    return parser


def _print_provider_summary(provider: str, result: dict[str, object]) -> None:
    print(f"\n[{provider}]")
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


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(asctime)s | %(levelname)s | %(message)s",
    )

    providers = [args.ats] if args.ats != "all" else ["greenhouse", "ashby", "lever", "bamboohr"]
    provider_results: dict[str, dict[str, object]] = {}

    for provider in providers:
        if provider == "greenhouse":
            result = asyncio.run(
                run_greenhouse_happy_path(
                    limit=args.limit,
                    target_location=args.target_location,
                    max_concurrency=args.greenhouse_max_concurrency,
                    rate_limit_per_sec=args.greenhouse_rate_limit,
                )
            )
        elif provider == "ashby":
            result = asyncio.run(
                run_ashby_happy_path(
                    limit=args.limit,
                    target_location=args.target_location,
                    max_concurrency=args.ashby_max_concurrency,
                    rate_limit_per_sec=args.ashby_rate_limit,
                )
            )
        elif provider == "lever":
            result = asyncio.run(
                run_lever_happy_path(
                    limit=args.limit,
                    target_location=args.target_location,
                    max_concurrency=args.lever_max_concurrency,
                    rate_limit_per_sec=args.lever_rate_limit,
                )
            )
        else:
            result = asyncio.run(
                run_bamboohr_happy_path(
                    limit=args.limit,
                    target_location=args.target_location,
                    max_concurrency=args.bamboohr_max_concurrency,
                    rate_limit_per_sec=args.bamboohr_rate_limit,
                )
            )
        provider_results[provider] = result
        _print_provider_summary(provider, result)

    print(
        "\nCompleted providers: "
        + ", ".join(providers)
        + " | total_matches="
        + str(
            sum(
                int(provider_results[provider]["matches_count"])
                for provider in providers
            )
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
