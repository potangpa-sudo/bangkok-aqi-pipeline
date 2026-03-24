select
    cast(element1 as timestamp) as forecast_timestamp_local,
    cast(element2 as double) as pm25,
    cast(element3 as double) as pm10,
    cast(element4 as integer) as us_aqi,
    latitude,
    longitude,
    raw_file_name
from (
    select
        unnest(
            list_zip(hourly.time, hourly.pm2_5, hourly.pm10, hourly.us_aqi),
            recursive := true
        ),
        cast(latitude as double) as latitude,
        cast(longitude as double) as longitude,
        filename as raw_file_name
    from read_json_auto('{{ var("raw_aqi_glob") }}', filename = true)
)
