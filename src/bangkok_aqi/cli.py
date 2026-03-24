from __future__ import annotations

import argparse

from bangkok_aqi.extract import run_extract


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Bangkok AQI pipeline commands")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("extract", help="Fetch AQI data and land raw parquet files")
    return parser


def main() -> None:
    args = build_parser().parse_args()

    if args.command == "extract":
        run_extract()


if __name__ == "__main__":
    main()
