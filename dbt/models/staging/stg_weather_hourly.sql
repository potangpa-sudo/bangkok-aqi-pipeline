select
    forecast_timestamp_local,
    cast(forecast_timestamp_local as date) as forecast_date_local,
    temperature_c,
    relative_humidity,
    wind_speed_kph,
    split_part(replace(raw_file_name, '.json', ''), '_raw_', 2) as ingest_time_utc,
    'open-meteo-weather' as source_system,
    latitude,
    longitude,
    raw_file_name
from {{ ref("base_weather_hourly_exploded") }}
