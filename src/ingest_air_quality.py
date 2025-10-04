from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path
import json

import pandas as pd
import requests

from .config import Settings


AIR_QUALITY_ENDPOINT = "https://air-quality-api.open-meteo.com/v1/air-quality"


def _build_params(settings: Settings) -> dict:
    now = datetime.now()
    params = {
        "latitude": settings.latitude,
        "longitude": settings.longitude,
        "hourly": "pm10,pm2_5,carbon_monoxide,ozone,nitrogen_dioxide,sulphur_dioxide",
        "timezone": settings.timezone,
    }
    if settings.bootstrap_hours <= 168:
        start = now - timedelta(hours=settings.bootstrap_hours)
        params["start_date"] = start.strftime("%Y-%m-%d")
        params["end_date"] = now.strftime("%Y-%m-%d")
    else:
        days = min(max(settings.bootstrap_hours // 24 + 1, 2), 7)
        params["past_days"] = days
    return params


def _write_raw_payload(payload: dict, target_path: Path) -> None:
    target_path.parent.mkdir(parents=True, exist_ok=True)
    with target_path.open("w", encoding="utf-8") as f:
        json.dump(payload, f)


def fetch_air_quality(settings: Settings) -> pd.DataFrame:
    """Fetch hourly air-quality readings and return them as a DataFrame."""

    params = _build_params(settings)
    response = requests.get(AIR_QUALITY_ENDPOINT, params=params, timeout=30)
    if response.status_code != 200:
        raise RuntimeError(
            f"Air quality API request failed with status {response.status_code}: {response.text[:200]}"
        )

    payload = response.json()
    timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    raw_file = settings.raw_dir / f"air_quality_{timestamp}.json"
    _write_raw_payload(payload, raw_file)

    hourly = payload.get("hourly")
    if not hourly:
        raise RuntimeError("Air quality payload missing 'hourly' section")

    df = pd.DataFrame(hourly)
    if df.empty:
        raise RuntimeError("Air quality payload returned no hourly data")

    df["time"] = pd.to_datetime(df["time"], format="%Y-%m-%dT%H:%M", errors="coerce")
    df = df.dropna(subset=["time"]).copy()
    df.sort_values("time", inplace=True)

    cutoff = pd.Timestamp.now(tz=settings.timezone) - pd.Timedelta(hours=settings.bootstrap_hours)
    df["time"] = df["time"].dt.tz_localize(settings.timezone, nonexistent="shift_forward", ambiguous="NaT")
    df = df.dropna(subset=["time"])
    df = df[df["time"] >= cutoff]

    df["latitude"] = settings.latitude
    df["longitude"] = settings.longitude
    df["ingested_at"] = pd.Timestamp.utcnow()

    numeric_cols = [
        "pm10",
        "pm2_5",
        "carbon_monoxide",
        "ozone",
        "nitrogen_dioxide",
        "sulphur_dioxide",
    ]
    df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors="coerce")

    df.dropna(subset=["pm2_5"], inplace=True)
    df.reset_index(drop=True, inplace=True)
    return df


__all__ = ["fetch_air_quality"]
