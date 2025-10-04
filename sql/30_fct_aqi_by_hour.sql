CREATE OR REPLACE TABLE fct.aqi_by_hour AS
WITH hours AS (
    SELECT weather_hour AS hour_local FROM stg.stg_weather
    UNION
    SELECT aq_hour AS hour_local FROM stg.stg_air_quality
),
combined AS (
    SELECT
        h.hour_local,
        w.temperature_2m,
        w.relative_humidity_2m,
        w.precipitation,
        w.wind_speed_10m,
        a.pm2_5,
        a.pm10,
        a.carbon_monoxide,
        a.ozone,
        a.nitrogen_dioxide,
        a.sulphur_dioxide
    FROM hours h
    LEFT JOIN stg.stg_weather w ON h.hour_local = w.weather_hour
    LEFT JOIN stg.stg_air_quality a ON h.hour_local = a.aq_hour
)
SELECT
    hour_local,
    CAST(hour_local AS DATE) AS date_local,
    temperature_2m,
    relative_humidity_2m,
    precipitation,
    wind_speed_10m,
    pm2_5,
    pm10,
    carbon_monoxide,
    ozone,
    nitrogen_dioxide,
    sulphur_dioxide,
    CASE
        WHEN pm2_5 IS NULL THEN NULL
        ELSE ROUND(pm2_5 * 4)
    END AS pm25_aqi_proxy
FROM combined
ORDER BY hour_local;
