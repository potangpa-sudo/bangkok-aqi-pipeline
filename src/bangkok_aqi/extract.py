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


def build_raw_object_path(ingested_at: datetime) -> str:
    return (
        f"raw/ingest_date={ingested_at:%Y-%m-%d}/"
        f"bangkok_aqi_raw_{ingested_at:%Y%m%dT%H%M%SZ}.parquet"
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

    payload = fetch_hourly_payload(active_settings)
    frame = build_hourly_frame(payload, ingested_at, active_settings)
    object_path = build_raw_object_path(ingested_at)
    save_raw_frame(frame, storage, object_path)

    LOGGER.info(
        "Saved %s AQI rows to %s using %s storage",
        len(frame),
        object_path,
        storage.backend_name,
    )
    return object_path
