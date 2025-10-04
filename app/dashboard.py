from __future__ import annotations

from pathlib import Path

import duckdb
import pandas as pd
import streamlit as st

from src.config import get_settings


st.set_page_config(page_title="Bangkok AQI Dashboard", layout="wide")
settings = get_settings()


@st.cache_data(ttl=300)
def load_daily_snapshot() -> pd.DataFrame:
    db_path = Path(settings.duckdb_path)
    if not db_path.exists():
        return pd.DataFrame()

    conn = duckdb.connect(str(db_path), read_only=True)
    try:
        query = "SELECT * FROM mart.daily_aqi_weather ORDER BY date"
        df = conn.execute(query).fetchdf()
    except duckdb.CatalogException:
        df = pd.DataFrame()
    finally:
        conn.close()

    if not df.empty:
        df["date"] = pd.to_datetime(df["date"]).dt.date
    return df


def format_metric(value: float | None, precision: int = 1, suffix: str = "") -> str:
    if value is None or pd.isna(value):
        return "n/a"
    return f"{value:.{precision}f}{suffix}"


def main() -> None:
    st.title("Bangkok Weather & Air Quality")
    st.caption("Proxy AQI derived from PM2.5 — informational only, not an official measure.")

    df = load_daily_snapshot()
    if df.empty:
        st.warning("Run `make run` to populate the warehouse before launching the dashboard.")
        return

    latest = df.iloc[-1]

    kpi_cols = st.columns(3)
    kpi_cols[0].metric(
        "Latest Avg PM2.5 (µg/m³)",
        format_metric(latest.get("avg_pm2_5")),
        help="Daily average PM2.5 concentration."
    )
    kpi_cols[1].metric(
        "Latest Avg Temp (°C)",
        format_metric(latest.get("avg_temperature_c")),
        help="Daily average 2m air temperature."
    )
    kpi_cols[2].metric(
        "Latest Avg Humidity (%)",
        format_metric(latest.get("avg_relative_humidity")),
        help="Daily average relative humidity at 2m."
    )

    st.subheader("Daily Trends")
    trend_df = df.set_index(pd.to_datetime(df["date"]))[
        ["avg_pm2_5", "avg_temperature_c"]
    ].dropna(how="all")
    if trend_df.empty:
        st.info("Not enough data for trend charts yet.")
    else:
        st.line_chart(trend_df, height=300)

    st.subheader("PM2.5 Proxy AQI by Day")
    proxy_df = df.set_index(pd.to_datetime(df["date"]))[["avg_pm25_aqi_proxy"]]
    st.bar_chart(proxy_df, height=300)

    st.subheader("Recent Daily Observations")
    st.dataframe(df.tail(10), use_container_width=True)


if __name__ == "__main__":
    main()
