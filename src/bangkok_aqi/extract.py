from __future__ import annotations

import logging
from datetime import datetime, timezone
from io import BytesIO
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


class AQIPayloadValidationError(ValueError):
    """Raised when the upstream hourly AQI payload is structurally invalid."""


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


def fetch_hourly_payload(settings: Settings, session: Session | None = None) -> dict[str, Any]:
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
    return response.json()


def fetch_weather_payload(settings: Settings, session: Session | None = None) -> dict[str, Any]:
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
    return response.json()


def build_hourly_frame(
    payload: dict[str, Any], ingested_at: datetime, settings: Settings
) -> pd.DataFrame:
    hourly = payload.get("hourly")
    if not hourly:
        raise ValueError("Response payload does not contain an hourly section.")

    frame = pd.DataFrame(hourly)
    frame["ingest_time_utc"] = ingested_at.isoformat()
    frame["source_system"] = "open-meteo"
    frame["latitude"] = settings.latitude
    frame["longitude"] = settings.longitude
    return frame


def build_weather_frame(
    payload: dict[str, Any], ingested_at: datetime, settings: Settings
) -> pd.DataFrame:
    hourly = payload.get("hourly")
    if not hourly:
        raise ValueError("Weather payload does not contain an hourly section.")

    frame = pd.DataFrame(hourly)
    frame["ingest_time_utc"] = ingested_at.isoformat()
    frame["source_system"] = "open-meteo-weather"
    frame["latitude"] = settings.latitude
    frame["longitude"] = settings.longitude
    return frame


def validate_hourly_frame(frame: pd.DataFrame) -> None:
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


def validate_weather_frame(frame: pd.DataFrame) -> None:
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
    return (
        f"raw/ingest_date={ingested_at:%Y-%m-%d}/"
        f"bangkok_{dataset}_raw_{ingested_at:%Y%m%dT%H%M%SZ}.parquet"
    )


def save_raw_frame(frame: pd.DataFrame, storage: StorageClient, object_path: str) -> None:
    buffer = BytesIO()
    frame.to_parquet(buffer, index=False)
    storage.save_bytes(object_path, buffer.getvalue())


def run_extract(settings: Settings | None = None) -> str:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    active_settings = settings or get_settings()
    storage = StorageClient(active_settings)
    ingested_at = datetime.now(timezone.utc)

    session = build_session()

    aqi_payload = fetch_hourly_payload(active_settings, session=session)
    aqi_frame = build_hourly_frame(aqi_payload, ingested_at, active_settings)
    validate_hourly_frame(aqi_frame)
    aqi_object_path = build_raw_object_path(ingested_at, dataset="aqi")
    save_raw_frame(aqi_frame, storage, aqi_object_path)

    weather_payload = fetch_weather_payload(active_settings, session=session)
    weather_frame = build_weather_frame(weather_payload, ingested_at, active_settings)
    validate_weather_frame(weather_frame)
    weather_object_path = build_raw_object_path(ingested_at, dataset="weather")
    save_raw_frame(weather_frame, storage, weather_object_path)

    LOGGER.info(
        "Saved %s AQI rows to %s and %s weather rows to %s using %s storage",
        len(aqi_frame),
        aqi_object_path,
        len(weather_frame),
        weather_object_path,
        storage.backend_name,
    )
    return aqi_object_path
