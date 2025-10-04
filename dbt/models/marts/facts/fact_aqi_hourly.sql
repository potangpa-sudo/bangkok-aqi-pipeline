{{
    config(
        materialized='incremental',
        unique_key='event_hour',
        partition_by={
            'field': 'event_hour',
            'data_type': 'timestamp',
            'granularity': 'hour'
        },
        cluster_by=['date_local'],
        tags=['fact', 'hourly']
    )
}}

-- Fact table combining weather and air quality at hourly grain

WITH weather AS (
    SELECT * FROM {{ ref('stg_weather') }}
    {% if is_incremental() %}
        WHERE event_hour > (SELECT MAX(event_hour) FROM {{ this }})
    {% endif %}
),

aqi AS (
    SELECT * FROM {{ ref('stg_aqi') }}
    {% if is_incremental() %}
        WHERE event_hour > (SELECT MAX(event_hour) FROM {{ this }})
    {% endif %}
),

datetime AS (
    SELECT * FROM {{ ref('dim_datetime') }}
)

SELECT
    -- Time dimension
    w.event_hour,
    w.date_local,
    w.hour_local,
    dt.day_name,
    dt.is_weekend,
    dt.is_daytime,
    dt.is_rush_hour,
    
    -- Location
    COALESCE(w.latitude, a.latitude) AS latitude,
    COALESCE(w.longitude, a.longitude) AS longitude,
    
    -- Weather metrics
    w.temperature_celsius,
    w.temperature_fahrenheit,
    w.humidity_percent,
    w.precipitation_mm,
    w.wind_speed_ms,
    w.wind_speed_kmh,
    w.wind_direction_degrees,
    
    -- Air quality metrics
    a.pm10,
    a.pm2_5,
    a.carbon_monoxide,
    a.nitrogen_dioxide,
    a.sulphur_dioxide,
    a.ozone,
    a.us_aqi,
    a.european_aqi,
    a.us_aqi_category,
    a.pm25_aqi_proxy,
    
    -- Data quality flags
    w.is_temperature_anomaly,
    w.is_humidity_anomaly,
    a.is_pm25_anomaly,
    a.is_aqi_anomaly,
    CASE WHEN w.event_hour IS NULL OR a.event_hour IS NULL THEN TRUE ELSE FALSE END AS is_incomplete_hour,
    
    -- Metadata
    COALESCE(w.data_source, a.data_source) AS data_source,
    COALESCE(w.ingested_at, a.ingested_at) AS ingested_at,
    CURRENT_TIMESTAMP() AS dbt_updated_at

FROM weather w
FULL OUTER JOIN aqi a
    ON w.event_hour = a.event_hour
LEFT JOIN datetime dt
    ON w.event_hour = dt.event_hour

-- Ensure we have at least one data source
WHERE w.event_hour IS NOT NULL OR a.event_hour IS NOT NULL
