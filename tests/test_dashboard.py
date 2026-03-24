from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path

import duckdb
import pandas as pd

from bangkok_aqi.dashboard import (
    build_daily_summary,
    build_map_frame,
    build_metric_options,
    classify_aqi,
    is_data_stale,
    load_hourly_aqi,
)


def test_classify_aqi_returns_expected_band() -> None:
    assert classify_aqi(42).label == "Good"
    assert classify_aqi(125).label == "Unhealthy for Sensitive Groups"
    assert classify_aqi(320).label == "Hazardous"


def test_build_daily_summary_rolls_up_hourly_forecasts() -> None:
    hourly = pd.DataFrame(
        {
            "forecast_date_local": [date(2026, 3, 24), date(2026, 3, 24), date(2026, 3, 25)],
            "us_aqi": [70, 110, 80],
            "pm25": [28.2, 35.8, 30.0],
            "pm10": [40.1, 50.2, 44.0],
            "temperature_c": [31.0, 33.0, 30.0],
            "relative_humidity": [60.0, 68.0, 72.0],
            "wind_speed_kph": [10.0, 14.0, 12.0],
        }
    )

    daily = build_daily_summary(hourly)

    assert daily.to_dict(orient="records") == [
        {
            "forecast_date_local": date(2026, 3, 24),
            "avg_aqi": 90.0,
            "max_aqi": 110,
            "avg_pm25": 32.0,
            "avg_pm10": 45.2,
            "avg_temperature_c": 32.0,
            "avg_relative_humidity": 64.0,
            "avg_wind_speed_kph": 12.0,
        },
        {
            "forecast_date_local": date(2026, 3, 25),
            "avg_aqi": 80.0,
            "max_aqi": 80,
            "avg_pm25": 30.0,
            "avg_pm10": 44.0,
            "avg_temperature_c": 30.0,
            "avg_relative_humidity": 72.0,
            "avg_wind_speed_kph": 12.0,
        },
    ]


def test_build_metric_options_includes_weather_series() -> None:
    hourly = pd.DataFrame(
        {
            "us_aqi": [42],
            "pm25": [12.3],
            "pm10": [20.5],
            "temperature_c": [31.5],
            "relative_humidity": [63.0],
            "wind_speed_kph": [12.1],
        }
    )

    assert build_metric_options(hourly) == {
        "us_aqi": "US AQI",
        "pm25": "PM2.5",
        "pm10": "PM10",
        "temperature_c": "Temperature (C)",
        "relative_humidity": "Relative Humidity (%)",
        "wind_speed_kph": "Wind Speed (km/h)",
    }


def test_load_hourly_aqi_backfills_missing_weather_columns(tmp_path: Path) -> None:
    duckdb_path = tmp_path / "legacy_dashboard.duckdb"

    with duckdb.connect(str(duckdb_path)) as connection:
        connection.execute(
            """
            create table fct_aqi_hourly as
            select
                timestamp '2026-03-24 00:00:00' as forecast_timestamp_local,
                date '2026-03-24' as forecast_date_local,
                28.2::double as pm25,
                40.1::double as pm10,
                70::integer as us_aqi,
                timestamp '2026-03-23 17:00:00' as last_ingested_at_utc,
                'open-meteo' as source_system,
                13.75::double as latitude,
                100.5::double as longitude
            """
        )

    hourly = load_hourly_aqi(duckdb_path)

    assert list(hourly.columns) == [
        "forecast_timestamp_local",
        "forecast_date_local",
        "pm25",
        "pm10",
        "us_aqi",
        "temperature_c",
        "relative_humidity",
        "wind_speed_kph",
        "last_ingested_at_utc",
        "source_system",
        "latitude",
        "longitude",
    ]
    assert hourly[["temperature_c", "relative_humidity", "wind_speed_kph"]].isna().all().all()


def test_is_data_stale_only_after_two_hours() -> None:
    now = pd.Timestamp("2026-03-24 12:00:00+00:00")

    assert not is_data_stale(now - timedelta(hours=2), now=now)
    assert is_data_stale(now - timedelta(hours=2, minutes=1), now=now)


def test_build_map_frame_uses_latest_forecast_coordinates() -> None:
    hourly = pd.DataFrame(
        {
            "latitude": [13.75, 13.75],
            "longitude": [100.5, 100.5],
            "us_aqi": [58, 72],
        }
    )

    map_frame = build_map_frame(hourly)

    assert map_frame.to_dict(orient="records") == [
        {"latitude": 13.75, "longitude": 100.5, "us_aqi": 58}
    ]
