CREATE OR REPLACE TABLE stg.stg_weather AS
WITH ranked AS (
    SELECT
        time,
        date_trunc('hour', time) AS weather_hour,
        temperature_2m,
        relative_humidity_2m,
        precipitation,
        wind_speed_10m,
        latitude,
        longitude,
        ingested_at,
        ROW_NUMBER() OVER (
            PARTITION BY date_trunc('hour', time)
            ORDER BY ingested_at DESC
        ) AS rn
    FROM raw.raw_weather
)
SELECT
    weather_hour,
    temperature_2m,
    relative_humidity_2m,
    precipitation,
    wind_speed_10m,
    latitude,
    longitude
FROM ranked
WHERE rn = 1;
