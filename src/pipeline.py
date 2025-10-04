from __future__ import annotations

import sys

from .config import get_settings
from .ingest_weather import fetch_weather
from .ingest_air_quality import fetch_air_quality
from .load_to_duckdb import load_dataframe
from .run_sql import run_all_sql


def main() -> None:
    settings = get_settings()
    settings.raw_dir.mkdir(parents=True, exist_ok=True)

    print("Fetching weather data...")
    weather_df = fetch_weather(settings)
    print(f"Fetched {len(weather_df)} weather rows")
    load_dataframe("raw.raw_weather", weather_df, settings)
    print("Weather data loaded into DuckDB")

    print("Fetching air quality data...")
    air_df = fetch_air_quality(settings)
    print(f"Fetched {len(air_df)} air-quality rows")
    load_dataframe("raw.raw_air_quality", air_df, settings)
    print("Air quality data loaded into DuckDB")

    print("Running transformation SQL models...")
    run_all_sql(settings)
    print("Transforms complete. Pipeline finished successfully.")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # fail loudly for visibility
        print(f"Pipeline failed: {exc}", file=sys.stderr)
        raise
