from __future__ import annotations

from pathlib import Path
from typing import Iterable, List
import duckdb

from .config import Settings, get_settings


def _list_sql_files(sql_dir: Path) -> List[Path]:
    return sorted(sql_dir.glob("*.sql"))


def _execute_script(conn: duckdb.DuckDBPyConnection, sql_text: str) -> None:
    statements = [stmt.strip() for stmt in sql_text.split(";") if stmt.strip()]
    for statement in statements:
        conn.execute(statement)


def run_all_sql(settings: Settings) -> None:
    sql_dir = settings.base_dir / "sql"
    if not sql_dir.exists():
        raise FileNotFoundError(f"SQL directory not found: {sql_dir}")

    files = _list_sql_files(sql_dir)
    if not files:
        raise RuntimeError("No SQL files found to execute")

    conn = duckdb.connect(str(settings.duckdb_path))
    try:
        for path in files:
            sql_text = path.read_text(encoding="utf-8")
            print(f"Executing SQL: {path.name}")
            _execute_script(conn, sql_text)
    finally:
        conn.close()


def main() -> None:
    settings = get_settings()
    run_all_sql(settings)


if __name__ == "__main__":
    main()
