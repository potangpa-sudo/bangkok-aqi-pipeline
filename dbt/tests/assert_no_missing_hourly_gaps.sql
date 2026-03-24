with ordered_forecasts as (
    select
        forecast_timestamp_local,
        lag(forecast_timestamp_local) over (
            order by forecast_timestamp_local
        ) as previous_forecast_timestamp_local
    from {{ ref("fct_aqi_hourly") }}
)

select *
from ordered_forecasts
where previous_forecast_timestamp_local is not null
  and datediff(
      'hour',
      previous_forecast_timestamp_local,
      forecast_timestamp_local
  ) <> 1
