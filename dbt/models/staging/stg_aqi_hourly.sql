with raw_source as (
    select
        cast(time as timestamp) as forecast_timestamp_local,
        cast(pm2_5 as double) as pm25,
        cast(pm10 as double) as pm10,
        cast(us_aqi as integer) as us_aqi,
        cast(ingest_time_utc as timestamp) as ingest_time_utc,
        cast(source_system as varchar) as source_system,
        cast(latitude as double) as latitude,
        cast(longitude as double) as longitude,
        filename as raw_file_name
    from read_parquet('{{ var("raw_aqi_glob") }}', union_by_name = true, filename = true)
)

select
    forecast_timestamp_local,
    cast(forecast_timestamp_local as date) as forecast_date_local,
    pm25,
    pm10,
    us_aqi,
    ingest_time_utc,
    source_system,
    latitude,
    longitude,
    raw_file_name
from raw_source
