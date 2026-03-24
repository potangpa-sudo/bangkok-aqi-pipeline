select
    cast(element1 as timestamp) as forecast_timestamp_local,
    cast(element2 as double) as temperature_c,
    cast(element3 as double) as relative_humidity,
    cast(element4 as double) as wind_speed_kph,
    latitude,
    longitude,
    raw_file_name
from (
    select
        unnest(
            list_zip(
                hourly.time,
                hourly.temperature_2m,
                hourly.relative_humidity_2m,
                hourly.wind_speed_10m
            ),
            recursive := true
        ),
        cast(latitude as double) as latitude,
        cast(longitude as double) as longitude,
        filename as raw_file_name
    from read_json_auto('{{ var("raw_weather_glob") }}', filename = true)
)
