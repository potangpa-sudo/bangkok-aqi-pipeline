{{
    config(
        materialized='view',
        tags=['staging', 'weather']
    )
}}

-- Staging model for weather data with light transformations

SELECT
    event_hour,
    latitude,
    longitude,
    
    -- Temperature conversions and rounding
    ROUND(temperature_2m, 2) AS temperature_celsius,
    ROUND((temperature_2m * 9/5) + 32, 2) AS temperature_fahrenheit,
    
    -- Humidity
    ROUND(relative_humidity_2m, 1) AS humidity_percent,
    
    -- Precipitation
    ROUND(precipitation, 2) AS precipitation_mm,
    ROUND(precipitation / 25.4, 2) AS precipitation_inches,
    
    -- Wind
    ROUND(wind_speed_10m, 2) AS wind_speed_ms,
    ROUND(wind_speed_10m * 3.6, 2) AS wind_speed_kmh,
    ROUND(wind_direction_10m, 1) AS wind_direction_degrees,
    
    -- Metadata
    source AS data_source,
    ingested_at,
    
    -- Derived fields
    DATE(event_hour) AS date_local,
    EXTRACT(HOUR FROM event_hour) AS hour_local,
    FORMAT_TIMESTAMP('%Y-%m-%d %H:00', event_hour) AS hour_label,
    
    -- Data quality flags
    CASE
        WHEN temperature_2m IS NULL THEN TRUE
        WHEN temperature_2m < -50 OR temperature_2m > 60 THEN TRUE
        ELSE FALSE
    END AS is_temperature_anomaly,
    
    CASE
        WHEN relative_humidity_2m IS NULL THEN TRUE
        WHEN relative_humidity_2m < 0 OR relative_humidity_2m > 100 THEN TRUE
        ELSE FALSE
    END AS is_humidity_anomaly

FROM {{ source('staging', 'weather_hourly') }}

-- Filter out obvious bad data
WHERE event_hour IS NOT NULL
  AND temperature_2m IS NOT NULL
  AND temperature_2m BETWEEN -50 AND 60
