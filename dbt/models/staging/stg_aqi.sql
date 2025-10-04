{{
    config(
        materialized='view',
        tags=['staging', 'aqi']
    )
}}

-- Staging model for air quality data with light transformations

SELECT
    event_hour,
    latitude,
    longitude,
    
    -- Pollutants (rounded)
    ROUND(pm10, 2) AS pm10,
    ROUND(pm2_5, 2) AS pm2_5,
    ROUND(carbon_monoxide, 2) AS carbon_monoxide,
    ROUND(nitrogen_dioxide, 2) AS nitrogen_dioxide,
    ROUND(sulphur_dioxide, 2) AS sulphur_dioxide,
    ROUND(ozone, 2) AS ozone,
    
    -- AQI indices
    us_aqi,
    european_aqi,
    
    -- Metadata
    source AS data_source,
    ingested_at,
    
    -- Derived fields
    DATE(event_hour) AS date_local,
    EXTRACT(HOUR FROM event_hour) AS hour_local,
    FORMAT_TIMESTAMP('%Y-%m-%d %H:00', event_hour) AS hour_label,
    
    -- AQI categories (US EPA)
    CASE
        WHEN us_aqi BETWEEN 0 AND 50 THEN 'Good'
        WHEN us_aqi BETWEEN 51 AND 100 THEN 'Moderate'
        WHEN us_aqi BETWEEN 101 AND 150 THEN 'Unhealthy for Sensitive Groups'
        WHEN us_aqi BETWEEN 151 AND 200 THEN 'Unhealthy'
        WHEN us_aqi BETWEEN 201 AND 300 THEN 'Very Unhealthy'
        WHEN us_aqi > 300 THEN 'Hazardous'
        ELSE 'Unknown'
    END AS us_aqi_category,
    
    -- Simple PM2.5 proxy AQI (matching local pipeline logic)
    CAST(ROUND(pm2_5 * 4) AS INT64) AS pm25_aqi_proxy,
    
    -- Data quality flags
    CASE
        WHEN pm2_5 IS NULL THEN TRUE
        WHEN pm2_5 < 0 OR pm2_5 > 1000 THEN TRUE
        ELSE FALSE
    END AS is_pm25_anomaly,
    
    CASE
        WHEN us_aqi IS NULL THEN TRUE
        WHEN us_aqi < 0 OR us_aqi > 500 THEN TRUE
        ELSE FALSE
    END AS is_aqi_anomaly

FROM {{ source('staging', 'aqi_hourly') }}

-- Filter out obvious bad data
WHERE event_hour IS NOT NULL
  AND pm2_5 IS NOT NULL
  AND pm2_5 >= 0
