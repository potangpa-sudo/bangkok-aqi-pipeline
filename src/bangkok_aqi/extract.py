from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

import pandas as pd
import requests
from requests import Session
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from bangkok_aqi.config import Settings, get_settings
from bangkok_aqi.storage import StorageClient

LOGGER = logging.getLogger(__name__)
AIR_QUALITY_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"
WEATHER_FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
REQUIRED_HOURLY_COLUMNS = ("time", "pm2_5", "pm10", "us_aqi")
METRIC_COLUMNS = ("pm2_5", "pm10", "us_aqi")
REQUIRED_WEATHER_COLUMNS = ("time", "temperature_2m", "relative_humidity_2m", "wind_speed_10m")
RAW_DATASET_FILE_PREFIXES = {
    "aqi": "bangkok_aqi_raw",
    "weather": "bangkok_weather_raw",
}


class AQIPayloadValidationError(ValueError):
    """Raised when the upstream hourly AQI payload is structurally invalid."""


@dataclass(frozen=True)
class RawPayload:
    payload: dict[str, Any]
    content: bytes


def build_session() -> Session:
    session = requests.Session()
    retry = Retry(
        total=3,
        connect=3,
        read=3,
        backoff_factor=1,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=frozenset({"GET"}),
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session


def fetch_aqi_payload(settings: Settings, session: Session | None = None) -> RawPayload:
    active_session = session or build_session()
    response = active_session.get(
        AIR_QUALITY_URL,
        params={
            "latitude": settings.latitude,
            "longitude": settings.longitude,
            "hourly": "pm2_5,pm10,us_aqi",
            "timezone": settings.timezone_name,
        },
        timeout=30,
    )
    response.raise_for_status()
    return RawPayload(payload=response.json(), content=response.content)


def fetch_weather_payload(settings: Settings, session: Session | None = None) -> RawPayload:
    active_session = session or build_session()
    response = active_session.get(
        WEATHER_FORECAST_URL,
        params={
            "latitude": settings.latitude,
            "longitude": settings.longitude,
            "hourly": "temperature_2m,relative_humidity_2m,wind_speed_10m",
            "timezone": settings.timezone_name,
        },
        timeout=30,
    )
    response.raise_for_status()
    return RawPayload(payload=response.json(), content=response.content)


def build_hourly_payload_frame(payload: dict[str, Any]) -> pd.DataFrame:
    hourly = payload.get("hourly")
    if not hourly:
        raise AQIPayloadValidationError("Response payload does not contain an hourly section.")

    return pd.DataFrame(hourly)


def build_weather_payload_frame(payload: dict[str, Any]) -> pd.DataFrame:
    hourly = payload.get("hourly")
    if not hourly:
        raise AQIPayloadValidationError("Weather payload does not contain an hourly section.")

    return pd.DataFrame(hourly)


def validate_hourly_payload(payload: dict[str, Any]) -> None:
    frame = build_hourly_payload_frame(payload)
    missing_columns = [column for column in REQUIRED_HOURLY_COLUMNS if column not in frame.columns]
    if missing_columns:
        formatted_columns = ", ".join(sorted(missing_columns))
        raise AQIPayloadValidationError(
            f"Hourly payload is missing required columns: {formatted_columns}."
        )

    if frame.empty:
        raise AQIPayloadValidationError("Hourly payload produced an empty frame.")

    parsed_timestamps = pd.to_datetime(frame["time"], errors="coerce")
    if parsed_timestamps.isna().any():
        raise AQIPayloadValidationError("Hourly payload contains invalid forecast timestamps.")

    if all(frame[column].isna().all() for column in METRIC_COLUMNS):
        raise AQIPayloadValidationError("Hourly payload does not contain any non-null AQI metrics.")


def validate_weather_payload(payload: dict[str, Any]) -> None:
    frame = build_weather_payload_frame(payload)
    missing_columns = [column for column in REQUIRED_WEATHER_COLUMNS if column not in frame.columns]
    if missing_columns:
        formatted_columns = ", ".join(sorted(missing_columns))
        raise AQIPayloadValidationError(
            f"Weather payload is missing required columns: {formatted_columns}."
        )

    if frame.empty:
        raise AQIPayloadValidationError("Weather payload produced an empty frame.")

    parsed_timestamps = pd.to_datetime(frame["time"], errors="coerce")
    if parsed_timestamps.isna().any():
        raise AQIPayloadValidationError("Weather payload contains invalid forecast timestamps.")


def build_raw_object_path(ingested_at: datetime, dataset: str = "aqi") -> str:
    file_prefix = RAW_DATASET_FILE_PREFIXES.get(dataset)
    if file_prefix is None:
        raise ValueError(f"Unsupported dataset '{dataset}'.")

    return (
        f"raw/{dataset}/ingest_date={ingested_at:%Y-%m-%d}/"
        f"{file_prefix}_{ingested_at:%Y%m%dT%H%M%SZ}.json"
    )


def save_raw_payload(raw_payload: bytes, storage: StorageClient, object_path: str) -> None:
    storage.save_bytes(object_path, raw_payload)


def extract_aqi_to_bronze(
    settings: Settings | None = None,
    session: Session | None = None,
    ingested_at: datetime | None = None,
) -> str:
    active_settings = settings or get_settings()
    active_session = session or build_session()
    active_ingested_at = ingested_at or datetime.now(timezone.utc)
    storage = StorageClient(active_settings)

    raw_payload = fetch_aqi_payload(active_settings, session=active_session)
    validate_hourly_payload(raw_payload.payload)
    object_path = build_raw_object_path(active_ingested_at, dataset="aqi")
    save_raw_payload(raw_payload.content, storage, object_path)
    LOGGER.info("Saved raw AQI payload to %s using %s storage", object_path, storage.backend_name)
    return object_path


def extract_weather_to_bronze(
    settings: Settings | None = None,
    session: Session | None = None,
    ingested_at: datetime | None = None,
) -> str:
    active_settings = settings or get_settings()
    active_session = session or build_session()
    active_ingested_at = ingested_at or datetime.now(timezone.utc)
    storage = StorageClient(active_settings)

    raw_payload = fetch_weather_payload(active_settings, session=active_session)
    validate_weather_payload(raw_payload.payload)
    object_path = build_raw_object_path(active_ingested_at, dataset="weather")
    save_raw_payload(raw_payload.content, storage, object_path)
    LOGGER.info(
        "Saved raw weather payload to %s using %s storage",
        object_path,
        storage.backend_name,
    )
    return object_path


def run_extract(settings: Settings | None = None) -> dict[str, str]:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    active_settings = settings or get_settings()
    ingested_at = datetime.now(timezone.utc)
    session = build_session()
    aqi_object_path = extract_aqi_to_bronze(
        settings=active_settings,
        session=session,
        ingested_at=ingested_at,
    )
    weather_object_path = extract_weather_to_bronze(
        settings=active_settings,
        session=session,
        ingested_at=ingested_at,
    )

    LOGGER.info(
        "Saved raw AQI payload to %s and raw weather payload to %s",
        aqi_object_path,
        weather_object_path,
    )
    return {"aqi": aqi_object_path, "weather": weather_object_path}
