select *
from {{ ref("fct_aqi_hourly") }}
where pm25 < 0
   or pm10 < 0
   or us_aqi < 0
