CREATE OR REPLACE TABLE stg.dim_datetime AS
WITH hours AS (
    SELECT weather_hour AS hour_local FROM stg.stg_weather
    UNION
    SELECT aq_hour AS hour_local FROM stg.stg_air_quality
)
SELECT
    hour_local,
    CAST(hour_local AS DATE) AS date_local,
    CAST(strftime(hour_local, '%H') AS INTEGER) AS hour_of_day,
    strftime(hour_local, '%A') AS day_name,
    CASE WHEN extract('dow' FROM hour_local) IN (0, 6) THEN TRUE ELSE FALSE END AS is_weekend
FROM hours;
