select *
from {{ ref("fct_aqi_hourly") }}
where (pm25 is not null and pm25 < 0)
   or (pm10 is not null and pm10 < 0)
   or (us_aqi is not null and (us_aqi < 0 or us_aqi > 500))
