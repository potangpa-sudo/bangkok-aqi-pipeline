with ranked_forecasts as (
    select
        *,
        row_number() over (
            partition by forecast_timestamp_local
            order by ingest_time_utc desc, raw_file_name desc
        ) as version_rank
    from {{ ref("stg_aqi_hourly") }}
),
ranked_weather as (
    select
        *,
        row_number() over (
            partition by forecast_timestamp_local
            order by ingest_time_utc desc, raw_file_name desc
        ) as version_rank
    from {{ ref("stg_weather_hourly") }}
)

select
    md5(
        cast(aqi.forecast_timestamp_local as varchar) || '|' || cast(aqi.ingest_time_utc as varchar)
    ) as record_key,
    aqi.forecast_timestamp_local,
    aqi.forecast_date_local,
    aqi.pm25,
    aqi.pm10,
    aqi.us_aqi,
    weather.temperature_c,
    weather.relative_humidity,
    weather.wind_speed_kph,
    aqi.ingest_time_utc as last_ingested_at_utc,
    aqi.source_system,
    aqi.latitude,
    aqi.longitude
from ranked_forecasts as aqi
left join ranked_weather as weather
    on aqi.forecast_timestamp_local = weather.forecast_timestamp_local
   and weather.version_rank = 1
where aqi.version_rank = 1
