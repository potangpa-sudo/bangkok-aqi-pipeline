{{
    config(
        materialized='table',
        partition_by={
            'field': 'date',
            'data_type': 'date',
            'granularity': 'day'
        },
        cluster_by=['year', 'month'],
        tags=['mart', 'daily', 'aggregate']
    )
}}

-- Daily aggregate mart for air quality and weather

SELECT
    date_local AS date,
    EXTRACT(YEAR FROM date_local) AS year,
    EXTRACT(MONTH FROM date_local) AS month,
    EXTRACT(DAY FROM date_local) AS day,
    ANY_VALUE(day_name) AS day_name,
    ANY_VALUE(is_weekend) AS is_weekend,
    
    -- Observation counts
    COUNT(*) AS hours_observed,
    COUNT(CASE WHEN NOT is_incomplete_hour THEN 1 END) AS hours_complete,
    COUNT(CASE WHEN is_daytime THEN 1 END) AS daytime_hours,
    COUNT(CASE WHEN is_rush_hour THEN 1 END) AS rush_hours,
    
    -- Weather aggregates
    ROUND(AVG(temperature_celsius), 2) AS avg_temperature_c,
    ROUND(MIN(temperature_celsius), 2) AS min_temperature_c,
    ROUND(MAX(temperature_celsius), 2) AS max_temperature_c,
    ROUND(AVG(humidity_percent), 1) AS avg_humidity_pct,
    ROUND(SUM(precipitation_mm), 2) AS total_precipitation_mm,
    ROUND(AVG(wind_speed_ms), 2) AS avg_wind_speed_ms,
    ROUND(MAX(wind_speed_ms), 2) AS max_wind_speed_ms,
    
    -- Air quality aggregates
    ROUND(AVG(pm2_5), 2) AS avg_pm2_5,
    ROUND(MIN(pm2_5), 2) AS min_pm2_5,
    ROUND(MAX(pm2_5), 2) AS max_pm2_5,
    ROUND(APPROX_QUANTILES(pm2_5, 100)[OFFSET(95)], 2) AS p95_pm2_5,
    
    ROUND(AVG(pm10), 2) AS avg_pm10,
    ROUND(AVG(ozone), 2) AS avg_ozone,
    ROUND(AVG(nitrogen_dioxide), 2) AS avg_no2,
    
    -- AQI aggregates
    ROUND(AVG(us_aqi), 0) AS avg_us_aqi,
    MAX(us_aqi) AS max_us_aqi,
    ROUND(AVG(pm25_aqi_proxy), 0) AS avg_pm25_aqi_proxy,
    MAX(pm25_aqi_proxy) AS max_pm25_aqi_proxy,
    
    -- Most common AQI category
    APPROX_TOP_COUNT(us_aqi_category, 1)[OFFSET(0)].value AS most_common_aqi_category,
    
    -- Unhealthy hours (AQI > 100)
    COUNTIF(us_aqi > 100) AS unhealthy_hours,
    COUNTIF(us_aqi > 150) AS very_unhealthy_hours,
    
    -- Hour with max PM2.5
    ANY_VALUE(event_hour ORDER BY pm2_5 DESC LIMIT 1) AS max_pm25_hour,
    
    -- Data quality
    COUNTIF(is_temperature_anomaly) AS temperature_anomaly_hours,
    COUNTIF(is_pm25_anomaly) AS pm25_anomaly_hours,
    COUNTIF(is_incomplete_hour) AS incomplete_hours,
    
    -- Metadata
    MAX(ingested_at) AS last_ingested_at,
    CURRENT_TIMESTAMP() AS dbt_updated_at

FROM {{ ref('fact_aqi_hourly') }}

GROUP BY date_local

ORDER BY date_local DESC
