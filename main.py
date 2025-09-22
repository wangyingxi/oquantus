"""Command line entry point for the Oquantus screening tool."""

from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path
from typing import Iterable

from oquantus.config import AppConfig, load_config
from oquantus.screening import ScreeningEngine


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the daily stock screening workflow.")
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("config/default.yaml"),
        help="Path to the YAML configuration file.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Optional maximum number of symbols to process.",
    )
    parser.add_argument(
        "--today",
        type=str,
        default=None,
        help="Override today's date in YYYY-MM-DD format (useful for backfilling).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config: AppConfig = load_config(args.config)
    base_path = args.config.parent
    engine = ScreeningEngine.from_config(config, base_path)
    symbols = config.all_symbols(base_path)
    if args.limit:
        symbols = symbols[: args.limit]
    today = date.fromisoformat(args.today) if args.today else date.today()
    start_date, end_date = config.fetcher.period(today)
    candidates = engine.screen(symbols, start_date, end_date)
    for candidate in candidates:
        print(candidate.symbol)
        for result in candidate.results:
            metadata = ", ".join(f"{k}={v:.2f}" for k, v in result.metadata.items())
            print(f"  - {result.strategy}: score={result.score:.4f} ({metadata})")


if __name__ == "__main__":
    main()
