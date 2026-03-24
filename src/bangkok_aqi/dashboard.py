from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import duckdb
import pandas as pd


@dataclass(frozen=True)
class AQIBand:
    label: str
    color: str
    advisory: str


AQI_BANDS: tuple[tuple[int, AQIBand], ...] = (
    (
        50,
        AQIBand(
            label="Good",
            color="#2E8540",
            advisory="Air quality is considered satisfactory.",
        ),
    ),
    (
        100,
        AQIBand(
            label="Moderate",
            color="#D4A017",
            advisory="Acceptable for most people, with minor risk for sensitive groups.",
        ),
    ),
    (
        150,
        AQIBand(
            label="Unhealthy for Sensitive Groups",
            color="#E67E22",
            advisory="Sensitive groups should limit prolonged outdoor exertion.",
        ),
    ),
    (
        200,
        AQIBand(
            label="Unhealthy",
            color="#C0392B",
            advisory="Everyone may begin to experience health effects.",
        ),
    ),
    (
        300,
        AQIBand(
            label="Very Unhealthy",
            color="#7D3C98",
            advisory="Health alert conditions; outdoor activity should be reduced.",
        ),
    ),
)

HAZARDOUS_BAND = AQIBand(
    label="Hazardous",
    color="#6E2C00",
    advisory="Emergency conditions; avoid outdoor activity where possible.",
)

UNKNOWN_BAND = AQIBand(
    label="Unknown",
    color="#5C6770",
    advisory="AQI data is not available for this selection.",
)


def classify_aqi(value: float | int | None) -> AQIBand:
    if value is None or pd.isna(value):
        return UNKNOWN_BAND

    aqi = float(value)
    for upper_bound, band in AQI_BANDS:
        if aqi <= upper_bound:
            return band

    return HAZARDOUS_BAND


def warehouse_has_mart(duckdb_path: Path) -> bool:
    with duckdb.connect(str(duckdb_path), read_only=True) as connection:
        table_count = connection.execute(
            """
            select count(*)
            from information_schema.tables
            where table_schema = 'main' and table_name = 'fct_aqi_hourly'
            """
        ).fetchone()

    return bool(table_count and table_count[0])


def load_hourly_aqi(duckdb_path: Path) -> pd.DataFrame:
    with duckdb.connect(str(duckdb_path), read_only=True) as connection:
        hourly = connection.execute(
            """
            select
                forecast_timestamp_local,
                forecast_date_local,
                pm25,
                pm10,
                us_aqi,
                temperature_c,
                relative_humidity,
                wind_speed_kph,
                last_ingested_at_utc,
                source_system,
                latitude,
                longitude
            from fct_aqi_hourly
            order by forecast_timestamp_local
            """
        ).fetchdf()

    hourly["forecast_timestamp_local"] = pd.to_datetime(hourly["forecast_timestamp_local"])
    hourly["forecast_date_local"] = pd.to_datetime(hourly["forecast_date_local"]).dt.date
    hourly["last_ingested_at_utc"] = pd.to_datetime(hourly["last_ingested_at_utc"], utc=True)
    return hourly


def build_daily_summary(hourly: pd.DataFrame) -> pd.DataFrame:
    if hourly.empty:
        return pd.DataFrame(
            columns=[
                "forecast_date_local",
                "avg_aqi",
                "max_aqi",
                "avg_pm25",
                "avg_pm10",
                "avg_temperature_c",
                "avg_relative_humidity",
                "avg_wind_speed_kph",
            ]
        )

    return (
        hourly.groupby("forecast_date_local", as_index=False)
        .agg(
            avg_aqi=("us_aqi", "mean"),
            max_aqi=("us_aqi", "max"),
            avg_pm25=("pm25", "mean"),
            avg_pm10=("pm10", "mean"),
            avg_temperature_c=("temperature_c", "mean"),
            avg_relative_humidity=("relative_humidity", "mean"),
            avg_wind_speed_kph=("wind_speed_kph", "mean"),
        )
        .round(
            {
                "avg_aqi": 1,
                "max_aqi": 0,
                "avg_pm25": 1,
                "avg_pm10": 1,
                "avg_temperature_c": 1,
                "avg_relative_humidity": 1,
                "avg_wind_speed_kph": 1,
            }
        )
    )


def build_metric_options(hourly: pd.DataFrame) -> dict[str, str]:
    options: dict[str, str] = {"us_aqi": "US AQI"}

    if "pm25" in hourly.columns:
        options["pm25"] = "PM2.5"
    if "pm10" in hourly.columns:
        options["pm10"] = "PM10"
    if "temperature_c" in hourly.columns:
        options["temperature_c"] = "Temperature (C)"
    if "relative_humidity" in hourly.columns:
        options["relative_humidity"] = "Relative Humidity (%)"
    if "wind_speed_kph" in hourly.columns:
        options["wind_speed_kph"] = "Wind Speed (km/h)"

    return options


def melt_metrics(hourly: pd.DataFrame, metric_options: dict[str, str]) -> pd.DataFrame:
    chart_data = hourly.melt(
        id_vars=["forecast_timestamp_local"],
        value_vars=list(metric_options),
        var_name="metric_key",
        value_name="value",
    )
    chart_data["metric"] = chart_data["metric_key"].map(metric_options)
    return chart_data.drop(columns=["metric_key"])


def build_status_rows(hourly: pd.DataFrame) -> list[dict[str, Any]]:
    if hourly.empty:
        return []

    latest_row = hourly.iloc[0]
    peak_row = hourly.loc[hourly["us_aqi"].idxmax()]

    return [
        {"label": "Source system", "value": str(latest_row["source_system"])},
        {
            "label": "Coordinates",
            "value": f'{latest_row["latitude"]:.2f}, {latest_row["longitude"]:.2f}',
        },
        {
            "label": "Peak forecast hour",
            "value": peak_row["forecast_timestamp_local"].strftime("%Y-%m-%d %H:%M"),
        },
        {"label": "Peak AQI band", "value": classify_aqi(peak_row["us_aqi"]).label},
        {"label": "Temperature", "value": f'{latest_row["temperature_c"]:.1f} C'},
        {"label": "Wind speed", "value": f'{latest_row["wind_speed_kph"]:.1f} km/h'},
    ]
