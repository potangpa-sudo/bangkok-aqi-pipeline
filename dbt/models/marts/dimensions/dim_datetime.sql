{{
    config(
        materialized='table',
        tags=['dimension', 'time']
    )
}}

-- Datetime dimension table at hourly grain

WITH hour_spine AS (
    -- Generate hourly spine from earliest to latest data
    SELECT DISTINCT
        event_hour
    FROM {{ ref('stg_weather') }}
    
    UNION DISTINCT
    
    SELECT DISTINCT
        event_hour
    FROM {{ ref('stg_aqi') }}
)

SELECT
    event_hour,
    
    -- Date components
    DATE(event_hour) AS date_local,
    EXTRACT(YEAR FROM event_hour) AS year,
    EXTRACT(MONTH FROM event_hour) AS month,
    EXTRACT(DAY FROM event_hour) AS day,
    EXTRACT(DAYOFWEEK FROM event_hour) AS day_of_week,
    EXTRACT(DAYOFYEAR FROM event_hour) AS day_of_year,
    EXTRACT(WEEK FROM event_hour) AS week_of_year,
    
    -- Time components
    EXTRACT(HOUR FROM event_hour) AS hour,
    FORMAT_TIMESTAMP('%Y-%m-%d %H:00', event_hour) AS hour_label,
    
    -- Named components
    FORMAT_TIMESTAMP('%A', event_hour) AS day_name,
    FORMAT_TIMESTAMP('%B', event_hour) AS month_name,
    FORMAT_TIMESTAMP('%Y-Q%Q', event_hour) AS quarter,
    
    -- Boolean flags
    CASE WHEN EXTRACT(DAYOFWEEK FROM event_hour) IN (1, 7) THEN TRUE ELSE FALSE END AS is_weekend,
    CASE WHEN EXTRACT(HOUR FROM event_hour) BETWEEN 6 AND 18 THEN TRUE ELSE FALSE END AS is_daytime,
    CASE WHEN EXTRACT(HOUR FROM event_hour) BETWEEN 7 AND 9 OR EXTRACT(HOUR FROM event_hour) BETWEEN 17 AND 19 THEN TRUE ELSE FALSE END AS is_rush_hour,
    
    -- Relative indicators
    CASE WHEN DATE(event_hour) = CURRENT_DATE('Asia/Bangkok') THEN TRUE ELSE FALSE END AS is_today,
    CASE WHEN DATE(event_hour) = DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 1 DAY) THEN TRUE ELSE FALSE END AS is_yesterday

FROM hour_spine

ORDER BY event_hour
