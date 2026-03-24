from datetime import datetime, timezone
from pathlib import Path

from bangkok_aqi.config import Settings
from bangkok_aqi.extract import build_hourly_frame, build_raw_object_path


def build_settings() -> Settings:
    return Settings(
        latitude=13.75,
        longitude=100.5,
        timezone_name="Asia/Bangkok",
        data_dir=Path("/tmp/bangkok-aqi-data"),
        warehouse_dir=Path("/tmp/bangkok-aqi-warehouse"),
        azure_storage_connection_string=None,
        azure_storage_container_name="aqi-data",
    )


def test_build_raw_object_path_partitions_by_ingest_date() -> None:
    ingested_at = datetime(2026, 3, 24, 12, 34, 56, tzinfo=timezone.utc)
    object_path = build_raw_object_path(ingested_at)

    assert object_path == "raw/ingest_date=2026-03-24/bangkok_aqi_raw_20260324T123456Z.parquet"


def test_build_hourly_frame_adds_metadata_columns() -> None:
    payload = {
        "hourly": {
            "time": ["2026-03-24T00:00"],
            "pm2_5": [12.3],
            "pm10": [20.5],
            "us_aqi": [42],
        }
    }

    frame = build_hourly_frame(
        payload,
        datetime(2026, 3, 24, 0, 0, tzinfo=timezone.utc),
        build_settings(),
    )

    assert frame.to_dict(orient="records") == [
        {
            "time": "2026-03-24T00:00",
            "pm2_5": 12.3,
            "pm10": 20.5,
            "us_aqi": 42,
            "ingest_time_utc": "2026-03-24T00:00:00+00:00",
            "source_system": "open-meteo",
            "latitude": 13.75,
            "longitude": 100.5,
        }
    ]
