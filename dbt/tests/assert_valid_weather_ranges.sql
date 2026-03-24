select *
from {{ ref("fct_aqi_hourly") }}
where (relative_humidity is not null and (relative_humidity < 0 or relative_humidity > 100))
   or (wind_speed_kph is not null and wind_speed_kph < 0)
