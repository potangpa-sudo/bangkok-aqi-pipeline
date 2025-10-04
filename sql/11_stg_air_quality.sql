CREATE OR REPLACE TABLE stg.stg_air_quality AS
WITH ranked AS (
    SELECT
        time,
        date_trunc('hour', time) AS aq_hour,
        pm10,
        pm2_5,
        carbon_monoxide,
        ozone,
        nitrogen_dioxide,
        sulphur_dioxide,
        latitude,
        longitude,
        ingested_at,
        ROW_NUMBER() OVER (
            PARTITION BY date_trunc('hour', time)
            ORDER BY ingested_at DESC
        ) AS rn
    FROM raw.raw_air_quality
)
SELECT
    aq_hour,
    pm10,
    pm2_5,
    carbon_monoxide,
    ozone,
    nitrogen_dioxide,
    sulphur_dioxide,
    latitude,
    longitude
FROM ranked
WHERE rn = 1;
