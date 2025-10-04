from __future__ import annotations

from datetime import datetime, timedelta
import sys

import duckdb

from .config import get_settings


class TestFailure(Exception):
    """Raised when a data quality check fails."""


def _table_exists(conn: duckdb.DuckDBPyConnection, schema: str, table: str) -> bool:
    query = (
        "SELECT COUNT(*) FROM information_schema.tables "
        "WHERE upper(table_schema) = upper(?) AND upper(table_name) = upper(?)"
    )
    result = conn.execute(query, [schema, table]).fetchone()[0]
    return result > 0


def _ensure_not_empty(conn: duckdb.DuckDBPyConnection, qualified_table: str) -> None:
    count = conn.execute(f"SELECT COUNT(*) FROM {qualified_table}").fetchone()[0]
    if count == 0:
        raise TestFailure(f"Table {qualified_table} is empty")


def _ensure_recent(conn: duckdb.DuckDBPyConnection) -> None:
    query = "SELECT MAX(date) FROM mart.daily_aqi_weather"
    max_date = conn.execute(query).fetchone()[0]
    if max_date is None:
        raise TestFailure("mart.daily_aqi_weather has no rows")
    today = datetime.now().date()
    if today - max_date > timedelta(days=3):
        raise TestFailure("mart.daily_aqi_weather is stale (older than 3 days)")


def run_tests() -> None:
    settings = get_settings()
    conn = duckdb.connect(str(settings.duckdb_path))
    try:
        if not _table_exists(conn, "raw", "raw_weather"):
            raise TestFailure("raw.raw_weather table is missing")
        if not _table_exists(conn, "raw", "raw_air_quality"):
            raise TestFailure("raw.raw_air_quality table is missing")
        if not _table_exists(conn, "mart", "daily_aqi_weather"):
            raise TestFailure("mart.daily_aqi_weather table is missing")

        _ensure_not_empty(conn, "raw.raw_weather")
        _ensure_not_empty(conn, "raw.raw_air_quality")
        _ensure_not_empty(conn, "mart.daily_aqi_weather")
        _ensure_recent(conn)

        print("All data quality checks passed")
    finally:
        conn.close()


def main() -> None:
    try:
        run_tests()
    except TestFailure as exc:
        print(f"TEST FAILURE: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
