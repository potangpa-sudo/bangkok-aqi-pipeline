with raw_source as (
    select
        cast(time as timestamp) as forecast_timestamp_local,
        cast(temperature_2m as double) as temperature_c,
        cast(relative_humidity_2m as double) as relative_humidity,
        cast(wind_speed_10m as double) as wind_speed_kph,
        cast(ingest_time_utc as timestamp) as ingest_time_utc,
        cast(source_system as varchar) as source_system,
        cast(latitude as double) as latitude,
        cast(longitude as double) as longitude,
        filename as raw_file_name
    from read_parquet('{{ var("raw_weather_glob") }}', union_by_name = true, filename = true)
    where source_system = 'open-meteo-weather'
)

select
    forecast_timestamp_local,
    cast(forecast_timestamp_local as date) as forecast_date_local,
    temperature_c,
    relative_humidity,
    wind_speed_kph,
    ingest_time_utc,
    source_system,
    latitude,
    longitude,
    raw_file_name
from raw_source
