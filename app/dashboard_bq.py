"""
Streamlit dashboard for Bangkok AQI - BigQuery version.
Supports both local DuckDB (dev) and BigQuery (prod) modes.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Literal

import pandas as pd
import streamlit as st

# Determine mode from environment
MODE = os.getenv("MODE", "duckdb").lower()  # "duckdb" or "bigquery"

if MODE == "bigquery":
    from google.cloud import bigquery
    import pandas_gbq
    
    PROJECT_ID = os.getenv("GCP_PROJECT_ID")
    DATASET_MARTS = os.getenv("BQ_DATASET_MARTS", "marts_aqi")
else:
    import duckdb
    from src.config import get_settings
    settings = get_settings()


st.set_page_config(
    page_title="Bangkok AQI Dashboard",
    page_icon="🌤️",
    layout="wide",
    initial_sidebar_state="expanded"
)


@st.cache_data(ttl=300)
def load_daily_snapshot_bigquery() -> pd.DataFrame:
    """Load data from BigQuery."""
    try:
        query = f"""
        SELECT 
            date,
            hours_observed,
            avg_pm2_5,
            avg_temperature_c,
            avg_humidity_pct,
            total_precipitation_mm,
            avg_wind_speed_ms,
            max_pm2_5,
            avg_us_aqi,
            max_us_aqi,
            avg_pm25_aqi_proxy,
            most_common_aqi_category,
            unhealthy_hours,
            max_pm25_hour
        FROM `{PROJECT_ID}.{DATASET_MARTS}.mart_daily_aqi_weather`
        ORDER BY date DESC
        LIMIT 90
        """
        
        df = pandas_gbq.read_gbq(
            query,
            project_id=PROJECT_ID,
            progress_bar_type=None
        )
        
        if not df.empty:
            df["date"] = pd.to_datetime(df["date"]).dt.date
        
        return df
        
    except Exception as e:
        st.error(f"Failed to load data from BigQuery: {str(e)}")
        return pd.DataFrame()


@st.cache_data(ttl=300)
def load_daily_snapshot_duckdb() -> pd.DataFrame:
    """Load data from local DuckDB (dev mode)."""
    db_path = Path(settings.duckdb_path)
    if not db_path.exists():
        return pd.DataFrame()

    conn = duckdb.connect(str(db_path), read_only=True)
    try:
        query = "SELECT * FROM mart.daily_aqi_weather ORDER BY date DESC LIMIT 90"
        df = conn.execute(query).fetchdf()
    except duckdb.CatalogException:
        df = pd.DataFrame()
    finally:
        conn.close()

    if not df.empty:
        df["date"] = pd.to_datetime(df["date"]).dt.date
    return df


def load_daily_snapshot() -> pd.DataFrame:
    """Load data based on current mode."""
    if MODE == "bigquery":
        return load_daily_snapshot_bigquery()
    else:
        return load_daily_snapshot_duckdb()


def format_metric(value: float | None, precision: int = 1, suffix: str = "") -> str:
    """Format metric value with precision and suffix."""
    if value is None or pd.isna(value):
        return "n/a"
    return f"{value:.{precision}f}{suffix}"


def get_aqi_color(aqi: float) -> str:
    """Get color for AQI value (US EPA standard)."""
    if aqi <= 50:
        return "🟢 Good"
    elif aqi <= 100:
        return "🟡 Moderate"
    elif aqi <= 150:
        return "🟠 Unhealthy for Sensitive"
    elif aqi <= 200:
        return "🔴 Unhealthy"
    elif aqi <= 300:
        return "🟣 Very Unhealthy"
    else:
        return "🟤 Hazardous"


def main() -> None:
    """Main dashboard application."""
    
    # Sidebar
    st.sidebar.title("Bangkok AQI Dashboard")
    st.sidebar.caption(f"Mode: **{MODE.upper()}**")
    st.sidebar.markdown("---")
    
    # Load data
    with st.spinner("Loading data..."):
        df = load_daily_snapshot()
    
    if df.empty:
        st.warning(
            "No data available. "
            f"{'Run `make run` to populate the warehouse.' if MODE == 'duckdb' else 'Check BigQuery connection and data availability.'}"
        )
        return
    
    # Header
    st.title("🌤️ Bangkok Weather & Air Quality Dashboard")
    st.caption(
        "Real-time air quality and weather insights for Bangkok, Thailand. "
        "Data sourced from Open-Meteo API."
    )
    st.markdown("---")
    
    # Date filter in sidebar
    st.sidebar.subheader("Filters")
    date_range = st.sidebar.slider(
        "Date Range (days)",
        min_value=7,
        max_value=90,
        value=30,
        step=7
    )
    df_filtered = df.head(date_range).sort_values("date")
    
    # Latest data point
    latest = df.iloc[0]
    
    # KPI Cards
    st.subheader("📊 Latest Daily Metrics")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Avg PM2.5 (µg/m³)",
            format_metric(latest.get("avg_pm2_5"), 1),
            delta=None,
            help="Daily average PM2.5 concentration"
        )
        st.caption(f"Max: {format_metric(latest.get('max_pm2_5'), 1)} µg/m³")
    
    with col2:
        aqi = latest.get("avg_us_aqi", 0)
        st.metric(
            "Avg US AQI",
            format_metric(aqi, 0),
            delta=None,
            help="US EPA Air Quality Index"
        )
        st.caption(get_aqi_color(aqi))
    
    with col3:
        st.metric(
            "Avg Temperature (°C)",
            format_metric(latest.get("avg_temperature_c"), 1),
            delta=None,
            help="Daily average temperature at 2m"
        )
    
    with col4:
        st.metric(
            "Avg Humidity (%)",
            format_metric(latest.get("avg_humidity_pct"), 0, "%"),
            delta=None,
            help="Daily average relative humidity"
        )
    
    # Additional KPIs
    col5, col6, col7, col8 = st.columns(4)
    
    with col5:
        st.metric(
            "Precipitation (mm)",
            format_metric(latest.get("total_precipitation_mm"), 1),
            help="Total daily precipitation"
        )
    
    with col6:
        st.metric(
            "Avg Wind Speed (m/s)",
            format_metric(latest.get("avg_wind_speed_ms"), 1),
            help="Daily average wind speed at 10m"
        )
    
    with col7:
        st.metric(
            "Unhealthy Hours",
            int(latest.get("unhealthy_hours", 0)),
            help="Hours with AQI > 100"
        )
    
    with col8:
        st.metric(
            "Hours Observed",
            int(latest.get("hours_observed", 0)),
            help="Number of hours with data"
        )
    
    st.markdown("---")
    
    # Trend Charts
    st.subheader("📈 Trends")
    
    tab1, tab2, tab3 = st.tabs(["Air Quality", "Weather", "Combined"])
    
    with tab1:
        st.markdown("### PM2.5 & US AQI Trends")
        
        # Check for required columns
        if "avg_pm2_5" in df_filtered.columns and "avg_us_aqi" in df_filtered.columns:
            chart_data = df_filtered.set_index("date")[["avg_pm2_5", "avg_us_aqi"]].dropna()
            
            if not chart_data.empty:
                st.line_chart(chart_data, height=400)
            else:
                st.info("No air quality data available for selected range.")
        else:
            st.warning("Air quality columns not found in data.")
        
        # AQI Category Distribution
        if "most_common_aqi_category" in df_filtered.columns:
            st.markdown("### Most Common AQI Category by Day")
            category_counts = df_filtered["most_common_aqi_category"].value_counts()
            st.bar_chart(category_counts)
    
    with tab2:
        st.markdown("### Temperature & Humidity Trends")
        
        if "avg_temperature_c" in df_filtered.columns and "avg_humidity_pct" in df_filtered.columns:
            weather_data = df_filtered.set_index("date")[["avg_temperature_c", "avg_humidity_pct"]].dropna()
            
            if not weather_data.empty:
                st.line_chart(weather_data, height=400)
            else:
                st.info("No weather data available for selected range.")
        else:
            st.warning("Weather columns not found in data.")
    
    with tab3:
        st.markdown("### PM2.5 vs Temperature")
        
        if "avg_pm2_5" in df_filtered.columns and "avg_temperature_c" in df_filtered.columns:
            scatter_data = df_filtered[["avg_pm2_5", "avg_temperature_c"]].dropna()
            
            if not scatter_data.empty:
                st.scatter_chart(scatter_data.set_index("avg_temperature_c"), height=400)
            else:
                st.info("No combined data available for selected range.")
        else:
            st.warning("Required columns not found for combined view.")
    
    st.markdown("---")
    
    # Data Table
    st.subheader("📋 Daily Observations")
    
    # Column selection for display
    display_cols = [
        "date",
        "avg_pm2_5",
        "avg_us_aqi",
        "avg_temperature_c",
        "avg_humidity_pct",
        "total_precipitation_mm",
        "unhealthy_hours",
        "hours_observed"
    ]
    
    # Filter to only existing columns
    available_cols = [col for col in display_cols if col in df_filtered.columns]
    
    st.dataframe(
        df_filtered[available_cols].sort_values("date", ascending=False),
        use_container_width=True,
        height=400
    )
    
    # Footer
    st.markdown("---")
    st.caption(
        f"Data refreshed every 5 minutes. "
        f"Latest observation: {latest.get('date')}. "
        f"Running in **{MODE.upper()}** mode."
    )
    
    # Sidebar info
    st.sidebar.markdown("---")
    st.sidebar.subheader("About")
    st.sidebar.markdown(
        """
        This dashboard visualizes air quality and weather data for Bangkok, Thailand.
        
        **Data Sources:**
        - Weather: Open-Meteo Forecast API
        - Air Quality: Open-Meteo Air Quality API
        
        **Metrics:**
        - **PM2.5**: Fine particulate matter (µg/m³)
        - **US AQI**: US EPA Air Quality Index (0-500)
        - **Temperature**: 2-meter air temperature (°C)
        - **Humidity**: Relative humidity (%)
        
        **Pipeline:**
        - Ingestion: Cloud Run (FastAPI)
        - Storage: GCS (raw), BigQuery (marts)
        - Processing: Dataproc Spark + dbt
        - Orchestration: Cloud Composer (Airflow)
        """
    )


if __name__ == "__main__":
    main()
