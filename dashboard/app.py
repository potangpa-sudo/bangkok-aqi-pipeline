from __future__ import annotations

from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st

from bangkok_aqi.config import get_settings
from bangkok_aqi.dashboard import (
    build_daily_summary,
    build_metric_options,
    build_status_rows,
    classify_aqi,
    load_hourly_aqi,
    melt_metrics,
    warehouse_has_mart,
)

st.set_page_config(page_title="Bangkok AQI Dashboard", layout="wide")


def has_metric_data(frame: pd.DataFrame, column: str) -> bool:
    return column in frame.columns and not frame[column].isna().all()


def format_optional_metric(
    frame: pd.DataFrame,
    row: pd.Series,
    column: str,
    fmt: str,
    suffix: str = "",
) -> str:
    if not has_metric_data(frame, column) or pd.isna(row[column]):
        return "N/A"

    return f"{row[column]:{fmt}}{suffix}"

st.markdown(
    """
    <style>
    .stApp {
        background:
            radial-gradient(circle at top left, rgba(201, 106, 22, 0.12), transparent 28%),
            linear-gradient(180deg, #f6f2e8 0%, #fcfbf7 42%, #edf4ef 100%);
    }
    .block-container {
        padding-top: 2.2rem;
        padding-bottom: 2rem;
    }
    .hero-card {
        padding: 1.6rem 1.8rem;
        border-radius: 24px;
        background: linear-gradient(135deg, rgba(27, 36, 48, 0.95), rgba(64, 89, 74, 0.92));
        color: #f9faf8;
        box-shadow: 0 18px 36px rgba(27, 36, 48, 0.16);
        margin-bottom: 1rem;
    }
    .hero-eyebrow {
        font-size: 0.85rem;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        opacity: 0.78;
        margin-bottom: 0.45rem;
    }
    .hero-value {
        font-size: 3rem;
        font-weight: 700;
        line-height: 1;
        margin: 0 0 0.5rem 0;
    }
    .hero-copy {
        font-size: 1rem;
        max-width: 48rem;
        opacity: 0.92;
        margin: 0;
    }
    .status-card {
        background: rgba(255, 255, 255, 0.72);
        border: 1px solid rgba(27, 36, 48, 0.08);
        border-radius: 18px;
        padding: 1rem 1.1rem;
        height: 100%;
    }
    .status-label {
        color: #5c6770;
        font-size: 0.82rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.3rem;
    }
    .status-value {
        color: #1b2430;
        font-size: 1.05rem;
        font-weight: 600;
        line-height: 1.3;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

settings = get_settings()
duckdb_path = settings.duckdb_path


@st.cache_data(ttl=300, show_spinner=False)
def get_hourly_data(path: str) -> pd.DataFrame:
    return load_hourly_aqi(Path(path))


st.sidebar.title("Bangkok AQI")
st.sidebar.caption("Dashboard controls")

if st.sidebar.button("Refresh warehouse data", use_container_width=True):
    st.cache_data.clear()
    st.rerun()

if not duckdb_path.exists():
    st.error(
        (
            f"Warehouse file not found at `{duckdb_path}`. "
            "Run `bangkok-aqi extract` and `dbt build --project-dir dbt --profiles-dir dbt` first."
        )
    )
    st.stop()

if not warehouse_has_mart(duckdb_path):
    st.error(
        (
            "DuckDB is present, but the `fct_aqi_hourly` mart is missing. "
            "Run `dbt build --project-dir dbt --profiles-dir dbt` first."
        )
    )
    st.stop()

hourly = get_hourly_data(str(duckdb_path))

if hourly.empty:
    st.warning("The mart exists but contains no rows yet.")
    st.stop()

min_date = hourly["forecast_date_local"].min()
max_date = hourly["forecast_date_local"].max()
selected_dates = st.sidebar.date_input(
    "Forecast window",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
)

if isinstance(selected_dates, (tuple, list)):
    start_date, end_date = selected_dates
else:
    start_date = end_date = selected_dates

metric_options = build_metric_options(hourly)
selected_metric_keys = st.sidebar.multiselect(
    "Chart series",
    options=list(metric_options),
    default=list(metric_options),
    format_func=metric_options.get,
)

filtered = hourly[
    (hourly["forecast_date_local"] >= start_date)
    & (hourly["forecast_date_local"] <= end_date)
].copy()

if filtered.empty:
    st.warning("No AQI records match the selected date range.")
    st.stop()

if not selected_metric_keys:
    selected_metric_keys = ["us_aqi"]

next_forecast = filtered.iloc[0]
peak_forecast = filtered.loc[filtered["us_aqi"].idxmax()]
aqi_band = classify_aqi(next_forecast["us_aqi"])
comparison_row = filtered.iloc[1] if len(filtered) > 1 else filtered.iloc[0]
aqi_delta = next_forecast["us_aqi"] - comparison_row["us_aqi"]
next_forecast_time = next_forecast["forecast_timestamp_local"].strftime("%Y-%m-%d %H:%M")
hero_aqi_value = int(next_forecast["us_aqi"])

st.markdown(
    f"""
    <div class="hero-card">
        <div class="hero-eyebrow">DuckDB mart / Bangkok hourly forecast</div>
        <div class="hero-value" style="color: {aqi_band.color};">{hero_aqi_value} AQI</div>
        <p class="hero-copy">
            Next forecast hour is <strong>{next_forecast_time}</strong>.
            Air quality is currently in the <strong>{aqi_band.label}</strong> band.
            {aqi_band.advisory}
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

metric_columns = st.columns(4)
metric_columns[0].metric("Next forecast AQI", f"{hero_aqi_value}", f"{aqi_delta:+.0f}")
metric_columns[1].metric("Peak AQI in window", f'{int(peak_forecast["us_aqi"])}')
metric_columns[2].metric("Average PM2.5", f'{filtered["pm25"].mean():.1f}')
metric_columns[3].metric(
    "Temperature",
    format_optional_metric(filtered, next_forecast, "temperature_c", ".1f", " C"),
)

secondary_metric_columns = st.columns(3)
secondary_metric_columns[0].metric(
    "Relative humidity",
    format_optional_metric(filtered, next_forecast, "relative_humidity", ".0f", "%"),
)
secondary_metric_columns[1].metric(
    "Wind speed",
    format_optional_metric(filtered, next_forecast, "wind_speed_kph", ".1f", " km/h"),
)
secondary_metric_columns[2].metric(
    "Last ingestion (UTC)",
    filtered["last_ingested_at_utc"].max().strftime("%Y-%m-%d %H:%M"),
)

status_rows = build_status_rows(filtered)
status_columns = st.columns(len(status_rows))
for column, status in zip(status_columns, status_rows, strict=False):
    column.markdown(
        f"""
        <div class="status-card">
            <div class="status-label">{status["label"]}</div>
            <div class="status-value">{status["value"]}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

aqi_chart = (
    alt.Chart(filtered)
    .mark_line(point=True, strokeWidth=3, color="#C96A16")
    .encode(
        x=alt.X("forecast_timestamp_local:T", title="Forecast time"),
        y=alt.Y("us_aqi:Q", title="US AQI"),
        tooltip=[
            alt.Tooltip("forecast_timestamp_local:T", title="Forecast time"),
            alt.Tooltip("us_aqi:Q", title="US AQI"),
            alt.Tooltip("pm25:Q", title="PM2.5", format=".1f"),
            alt.Tooltip("pm10:Q", title="PM10", format=".1f"),
            alt.Tooltip("temperature_c:Q", title="Temperature (C)", format=".1f"),
            alt.Tooltip("relative_humidity:Q", title="Humidity (%)", format=".0f"),
            alt.Tooltip("wind_speed_kph:Q", title="Wind speed (km/h)", format=".1f"),
        ],
    )
    .properties(height=320, title="AQI Forecast Curve")
)

chart_data = melt_metrics(filtered, {key: metric_options[key] for key in selected_metric_keys})
pollutant_chart = (
    alt.Chart(chart_data)
    .mark_line(strokeWidth=2.5)
    .encode(
        x=alt.X("forecast_timestamp_local:T", title="Forecast time"),
        y=alt.Y("value:Q", title="Value"),
        color=alt.Color(
            "metric:N",
            scale=alt.Scale(
                domain=[
                    "US AQI",
                    "PM2.5",
                    "PM10",
                    "Temperature (C)",
                    "Relative Humidity (%)",
                    "Wind Speed (km/h)",
                ],
                range=["#C96A16", "#2E8540", "#1F618D", "#C0392B", "#5B7DB1", "#40594A"],
            ),
        ),
        tooltip=[
            alt.Tooltip("forecast_timestamp_local:T", title="Forecast time"),
            alt.Tooltip("metric:N", title="Series"),
            alt.Tooltip("value:Q", title="Value", format=".1f"),
        ],
    )
    .properties(height=320, title="Selected AQI and Particulate Series")
)

daily_summary = build_daily_summary(filtered)
daily_chart = (
    alt.Chart(daily_summary)
    .mark_bar(cornerRadiusTopLeft=6, cornerRadiusTopRight=6, color="#40594A")
    .encode(
        x=alt.X("forecast_date_local:T", title="Forecast date"),
        y=alt.Y("max_aqi:Q", title="Daily max AQI"),
        tooltip=[
            alt.Tooltip("forecast_date_local:T", title="Forecast date"),
            alt.Tooltip("avg_aqi:Q", title="Average AQI", format=".1f"),
            alt.Tooltip("max_aqi:Q", title="Max AQI", format=".0f"),
            alt.Tooltip("avg_pm25:Q", title="Average PM2.5", format=".1f"),
            alt.Tooltip("avg_pm10:Q", title="Average PM10", format=".1f"),
            alt.Tooltip("avg_temperature_c:Q", title="Average Temperature (C)", format=".1f"),
            alt.Tooltip(
                "avg_relative_humidity:Q", title="Average Humidity (%)", format=".1f"
            ),
            alt.Tooltip("avg_wind_speed_kph:Q", title="Average Wind Speed (km/h)", format=".1f"),
        ],
    )
    .properties(height=280, title="Daily Peak AQI")
)

left_column, right_column = st.columns((1.2, 1))
left_column.altair_chart(aqi_chart, use_container_width=True)
right_column.altair_chart(pollutant_chart, use_container_width=True)

st.altair_chart(daily_chart, use_container_width=True)

display_table = filtered[
    [
        "forecast_timestamp_local",
        "us_aqi",
        "pm25",
        "pm10",
        "temperature_c",
        "relative_humidity",
        "wind_speed_kph",
        "last_ingested_at_utc",
    ]
].rename(
    columns={
        "forecast_timestamp_local": "forecast_time_local",
        "temperature_c": "temperature_c",
        "relative_humidity": "relative_humidity",
        "wind_speed_kph": "wind_speed_kph",
        "last_ingested_at_utc": "last_ingested_utc",
    }
)

st.subheader("Forecast records")
st.dataframe(display_table, use_container_width=True, hide_index=True)
