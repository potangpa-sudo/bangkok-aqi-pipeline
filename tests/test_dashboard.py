from __future__ import annotations

from datetime import date

import pandas as pd

from bangkok_aqi.dashboard import build_daily_summary, build_metric_options, classify_aqi


def test_classify_aqi_returns_expected_band() -> None:
    assert classify_aqi(42).label == "Good"
    assert classify_aqi(125).label == "Unhealthy for Sensitive Groups"
    assert classify_aqi(320).label == "Hazardous"


def test_build_daily_summary_rolls_up_hourly_forecasts() -> None:
    hourly = pd.DataFrame(
        {
            "forecast_date_local": [date(2026, 3, 24), date(2026, 3, 24), date(2026, 3, 25)],
            "us_aqi": [70, 110, 80],
            "pm25": [28.2, 35.8, 30.0],
            "pm10": [40.1, 50.2, 44.0],
            "temperature_c": [31.0, 33.0, 30.0],
            "relative_humidity": [60.0, 68.0, 72.0],
            "wind_speed_kph": [10.0, 14.0, 12.0],
        }
    )

    daily = build_daily_summary(hourly)

    assert daily.to_dict(orient="records") == [
        {
            "forecast_date_local": date(2026, 3, 24),
            "avg_aqi": 90.0,
            "max_aqi": 110,
            "avg_pm25": 32.0,
            "avg_pm10": 45.2,
            "avg_temperature_c": 32.0,
            "avg_relative_humidity": 64.0,
            "avg_wind_speed_kph": 12.0,
        },
        {
            "forecast_date_local": date(2026, 3, 25),
            "avg_aqi": 80.0,
            "max_aqi": 80,
            "avg_pm25": 30.0,
            "avg_pm10": 44.0,
            "avg_temperature_c": 30.0,
            "avg_relative_humidity": 72.0,
            "avg_wind_speed_kph": 12.0,
        },
    ]


def test_build_metric_options_includes_weather_series() -> None:
    hourly = pd.DataFrame(
        columns=["us_aqi", "pm25", "pm10", "temperature_c", "relative_humidity", "wind_speed_kph"]
    )

    assert build_metric_options(hourly) == {
        "us_aqi": "US AQI",
        "pm25": "PM2.5",
        "pm10": "PM10",
        "temperature_c": "Temperature (C)",
        "relative_humidity": "Relative Humidity (%)",
        "wind_speed_kph": "Wind Speed (km/h)",
    }
