from __future__ import annotations

from datetime import date

import pandas as pd

from bangkok_aqi.dashboard import build_daily_summary, classify_aqi


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
        },
        {
            "forecast_date_local": date(2026, 3, 25),
            "avg_aqi": 80.0,
            "max_aqi": 80,
            "avg_pm25": 30.0,
            "avg_pm10": 44.0,
        },
    ]
