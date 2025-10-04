from __future__ import annotations

from typing import Iterable

import duckdb
import pandas as pd

from .config import Settings


def _ensure_schema(conn: duckdb.DuckDBPyConnection, qualified_table: str) -> None:
    schema = qualified_table.split(".")[0]
    conn.execute(f"CREATE SCHEMA IF NOT EXISTS {schema}")


def load_dataframe(table_name: str, df: pd.DataFrame, settings: Settings) -> None:
    """Append a DataFrame into DuckDB, replacing duplicate timestamps."""

    if df.empty:
        raise ValueError("load_dataframe received an empty DataFrame")
    if "time" not in df.columns:
        raise ValueError("DataFrame missing required 'time' column")

    df = df.copy()
    df.sort_values("time", inplace=True)
    df.drop_duplicates(subset=["time"], keep="last", inplace=True)

    settings.data_dir.mkdir(parents=True, exist_ok=True)
    conn = duckdb.connect(str(settings.duckdb_path))
    try:
        _ensure_schema(conn, table_name)
        conn.register("temp_df", df)
        conn.execute(
            f"CREATE TABLE IF NOT EXISTS {table_name} AS SELECT * FROM temp_df LIMIT 0"
        )
        conn.execute(f"DELETE FROM {table_name} WHERE time IN (SELECT time FROM temp_df)")
        conn.execute(f"INSERT INTO {table_name} SELECT * FROM temp_df")
    finally:
        conn.unregister("temp_df")
        conn.close()


__all__ = ["load_dataframe"]
