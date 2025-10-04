from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional
import os

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    """Container for runtime configuration."""

    latitude: float
    longitude: float
    bootstrap_hours: int
    timezone: str
    base_dir: Path
    data_dir: Path
    raw_dir: Path
    screenshots_dir: Path
    duckdb_path: Path


def _coerce_float(value: Optional[str], fallback: float) -> float:
    if value is None:
        return fallback
    try:
        return float(value)
    except ValueError as exc:
        raise ValueError(f"Cannot parse float from value '{value}'") from exc


def _coerce_int(value: Optional[str], fallback: int) -> int:
    if value is None:
        return fallback
    try:
        return int(value)
    except ValueError as exc:
        raise ValueError(f"Cannot parse int from value '{value}'") from exc


def get_settings() -> Settings:
    """Load configuration from environment variables with sensible defaults."""

    load_dotenv()

    base_dir = Path(__file__).resolve().parent.parent
    data_dir = base_dir / "data"
    raw_dir = data_dir / "raw"
    screenshots_dir = data_dir / "screenshots"
    duckdb_path = data_dir / "warehouse.duckdb"

    timezone = os.getenv("TIMEZONE", "Asia/Bangkok")
    latitude = _coerce_float(os.getenv("LAT"), 13.7563)
    longitude = _coerce_float(os.getenv("LON"), 100.5018)
    bootstrap_hours = _coerce_int(os.getenv("BOOTSTRAP_HOURS"), 72)

    return Settings(
        latitude=latitude,
        longitude=longitude,
        bootstrap_hours=bootstrap_hours,
        timezone=timezone,
        base_dir=base_dir,
        data_dir=data_dir,
        raw_dir=raw_dir,
        screenshots_dir=screenshots_dir,
        duckdb_path=duckdb_path,
    )


__all__ = ["Settings", "get_settings"]
