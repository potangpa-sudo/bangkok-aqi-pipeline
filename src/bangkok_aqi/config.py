from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    latitude: float
    longitude: float
    timezone_name: str
    data_dir: Path
    warehouse_dir: Path
    azure_storage_connection_string: str | None
    azure_storage_container_name: str
    alert_webhook_url: str | None

    @property
    def duckdb_path(self) -> Path:
        return self.warehouse_dir / "bangkok_aqi.duckdb"


def get_settings() -> Settings:
    repo_root = Path(
        os.getenv("BANGKOK_AQI_REPO_ROOT", Path(__file__).resolve().parents[2])
    ).resolve()
    data_dir = repo_root / "data"
    warehouse_dir = repo_root / "warehouse"
    data_dir.mkdir(parents=True, exist_ok=True)
    warehouse_dir.mkdir(parents=True, exist_ok=True)

    return Settings(
        latitude=float(os.getenv("AQI_LATITUDE", "13.75")),
        longitude=float(os.getenv("AQI_LONGITUDE", "100.5")),
        timezone_name=os.getenv("AQI_TIMEZONE", "Asia/Bangkok"),
        data_dir=data_dir,
        warehouse_dir=warehouse_dir,
        azure_storage_connection_string=os.getenv("AZURE_STORAGE_CONNECTION_STRING"),
        azure_storage_container_name=os.getenv("AZURE_STORAGE_CONTAINER_NAME", "aqi-data"),
        alert_webhook_url=os.getenv("ALERT_WEBHOOK_URL"),
    )
