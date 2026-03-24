from datetime import datetime, timezone
from pathlib import Path

import pytest

from bangkok_aqi.config import Settings
from bangkok_aqi.extract import (
    AQIPayloadValidationError,
    build_raw_object_path,
    save_raw_payload,
    validate_hourly_payload,
    validate_weather_payload,
)
from bangkok_aqi.storage import StorageClient


def build_settings(base_path: Path | None = None) -> Settings:
    root_path = base_path or Path("/tmp")
    return Settings(
        latitude=13.75,
        longitude=100.5,
        timezone_name="Asia/Bangkok",
        data_dir=root_path / "bangkok-aqi-data",
        warehouse_dir=root_path / "bangkok-aqi-warehouse",
        azure_storage_connection_string=None,
        azure_storage_container_name="aqi-data",
        alert_webhook_url=None,
    )


def test_build_raw_object_path_partitions_by_ingest_date() -> None:
    ingested_at = datetime(2026, 3, 24, 12, 34, 56, tzinfo=timezone.utc)
    object_path = build_raw_object_path(ingested_at)

    assert object_path == "raw/aqi/ingest_date=2026-03-24/bangkok_aqi_raw_20260324T123456Z.json"


def test_save_raw_payload_writes_exact_json_bytes(tmp_path: Path) -> None:
    settings = build_settings(tmp_path)
    storage = StorageClient(settings)
    object_path = build_raw_object_path(
        datetime(2026, 3, 24, 12, 34, 56, tzinfo=timezone.utc),
        dataset="aqi",
    )
    raw_payload = (
        b'{"hourly":{"time":["2026-03-24T00:00"],"pm2_5":[12.3],"pm10":[20.5],"us_aqi":[42]}}'
    )

    save_raw_payload(raw_payload, storage, object_path)

    assert (settings.data_dir / object_path).read_bytes() == raw_payload


def test_validate_hourly_payload_rejects_missing_required_columns() -> None:
    payload = {
        "hourly": {
            "time": ["2026-03-24T00:00"],
            "pm2_5": [12.3],
            "pm10": [20.5],
        }
    }

    with pytest.raises(AQIPayloadValidationError, match="missing required columns: us_aqi"):
        validate_hourly_payload(payload)


def test_validate_hourly_payload_rejects_invalid_timestamps() -> None:
    payload = {
        "hourly": {
            "time": ["not-a-timestamp"],
            "pm2_5": [12.3],
            "pm10": [20.5],
            "us_aqi": [42],
        }
    }

    with pytest.raises(AQIPayloadValidationError, match="invalid forecast timestamps"):
        validate_hourly_payload(payload)


def test_validate_hourly_payload_rejects_all_null_metrics() -> None:
    payload = {
        "hourly": {
            "time": ["2026-03-24T00:00"],
            "pm2_5": [None],
            "pm10": [None],
            "us_aqi": [None],
        }
    }

    with pytest.raises(
        AQIPayloadValidationError, match="does not contain any non-null AQI metrics"
    ):
        validate_hourly_payload(payload)


def test_build_raw_object_path_supports_weather_dataset() -> None:
    ingested_at = datetime(2026, 3, 24, 12, 34, 56, tzinfo=timezone.utc)

    assert (
        build_raw_object_path(ingested_at, dataset="weather")
        == "raw/weather/ingest_date=2026-03-24/bangkok_weather_raw_20260324T123456Z.json"
    )


def test_validate_hourly_payload_rejects_missing_hourly_section() -> None:
    with pytest.raises(AQIPayloadValidationError, match="does not contain an hourly section"):
        validate_hourly_payload({})


def test_validate_weather_payload_rejects_missing_required_columns() -> None:
    payload = {
        "hourly": {
            "time": ["2026-03-24T00:00"],
            "temperature_2m": [31.5],
            "wind_speed_10m": [12.1],
        }
    }

    with pytest.raises(
        AQIPayloadValidationError, match="missing required columns: relative_humidity_2m"
    ):
        validate_weather_payload(payload)


def test_validate_weather_payload_rejects_invalid_timestamps() -> None:
    payload = {
        "hourly": {
            "time": ["not-a-timestamp"],
            "temperature_2m": [31.5],
            "relative_humidity_2m": [63],
            "wind_speed_10m": [12.1],
        }
    }

    with pytest.raises(AQIPayloadValidationError, match="invalid forecast timestamps"):
        validate_weather_payload(payload)


def test_validate_weather_payload_rejects_missing_hourly_section() -> None:
    with pytest.raises(AQIPayloadValidationError, match="does not contain an hourly section"):
        validate_weather_payload({})
