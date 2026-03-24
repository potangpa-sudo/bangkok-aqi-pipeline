with ranked_forecasts as (
    select
        *,
        row_number() over (
            partition by forecast_timestamp_local
            order by ingest_time_utc desc, raw_file_name desc
        ) as version_rank
    from {{ ref("stg_aqi_hourly") }}
)

select
    md5(
        cast(forecast_timestamp_local as varchar) || '|' || cast(ingest_time_utc as varchar)
    ) as record_key,
    forecast_timestamp_local,
    forecast_date_local,
    pm25,
    pm10,
    us_aqi,
    ingest_time_utc as last_ingested_at_utc,
    source_system,
    latitude,
    longitude
from ranked_forecasts
where version_rank = 1
