CREATE OR REPLACE TABLE mart.daily_aqi_weather AS
SELECT
    date_local AS date,
    COUNT(*) AS hours_observed,
    AVG(pm2_5) AS avg_pm2_5,
    AVG(temperature_2m) AS avg_temperature_c,
    AVG(relative_humidity_2m) AS avg_relative_humidity,
    AVG(precipitation) AS avg_precipitation_mm,
    AVG(wind_speed_10m) AS avg_wind_speed_ms,
    MAX(pm2_5) AS max_pm2_5,
    AVG(pm25_aqi_proxy) AS avg_pm25_aqi_proxy,
    MAX(hour_local) AS last_observed_hour,
    CURRENT_TIMESTAMP AS refreshed_at
FROM fct.aqi_by_hour
GROUP BY date_local
ORDER BY date;
