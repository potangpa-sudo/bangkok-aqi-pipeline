select
    forecast_timestamp_local,
    cast(forecast_timestamp_local as date) as forecast_date_local,
    pm25,
    pm10,
    us_aqi,
    split_part(replace(raw_file_name, '.json', ''), '_raw_', 2) as ingest_time_utc,
    'open-meteo' as source_system,
    latitude,
    longitude,
    raw_file_name
from {{ ref("base_aqi_hourly_exploded") }}
