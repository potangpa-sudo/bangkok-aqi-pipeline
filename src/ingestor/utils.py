"""
Utility functions for partitioning, timestamps, and API calls.
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Dict, Any, Tuple

import requests

logger = logging.getLogger(__name__)


def get_partition_path(dt: datetime) -> Tuple[str, str]:
    """
    Generate partition path components from datetime.
    
    Args:
        dt: Datetime object (should be timezone-aware)
        
    Returns:
        Tuple of (date_str, hour_str) like ("2025-10-05", "14")
    """
    # Ensure timezone-aware
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    
    date_str = dt.strftime("%Y-%m-%d")
    hour_str = dt.strftime("%H")
    
    return date_str, hour_str


def fetch_open_meteo_data(
    base_url: str,
    endpoint: str,
    latitude: float,
    longitude: float,
    timezone: str,
    data_type: str,
    timeout: int = 30
) -> Dict[str, Any]:
    """
    Fetch data from Open-Meteo API.
    
    Args:
        base_url: Base API URL
        endpoint: API endpoint (forecast or air-quality)
        latitude: Location latitude
        longitude: Location longitude
        timezone: Timezone name
        data_type: Type of data (weather or air_quality)
        timeout: Request timeout in seconds
        
    Returns:
        API response as dictionary
    """
    try:
        url = f"{base_url}/{endpoint}"
        
        if data_type == "weather":
            params = {
                "latitude": latitude,
                "longitude": longitude,
                "hourly": "temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m,wind_direction_10m",
                "timezone": timezone,
                "past_hours": 1,
                "forecast_hours": 1,
            }
        elif data_type == "air_quality":
            params = {
                "latitude": latitude,
                "longitude": longitude,
                "hourly": "pm10,pm2_5,carbon_monoxide,nitrogen_dioxide,sulphur_dioxide,ozone,us_aqi,european_aqi",
                "timezone": timezone,
                "past_hours": 1,
                "forecast_hours": 1,
            }
        else:
            raise ValueError(f"Unknown data_type: {data_type}")
        
        logger.info(f"Fetching {data_type} from {url}")
        response = requests.get(url, params=params, timeout=timeout)
        response.raise_for_status()
        
        data = response.json()
        
        # Add metadata
        from datetime import timezone as tz
        data["_metadata"] = {
            "fetched_at": datetime.now(tz.utc).isoformat(),
            "data_type": data_type,
            "latitude": latitude,
            "longitude": longitude,
        }
        
        return data
        
    except requests.RequestException as e:
        logger.error(f"Failed to fetch {data_type}: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error fetching {data_type}: {str(e)}")
        raise


def parse_partition_from_path(gcs_path: str) -> Tuple[str, str]:
    """
    Parse date and hour from GCS partition path.
    
    Args:
        gcs_path: GCS path like "gs://bucket/date=2025-10-05/hour=14/file.json"
        
    Returns:
        Tuple of (date_str, hour_str)
    """
    import re
    
    date_match = re.search(r'date=(\d{4}-\d{2}-\d{2})', gcs_path)
    hour_match = re.search(r'hour=(\d{2})', gcs_path)
    
    if not date_match or not hour_match:
        raise ValueError(f"Could not parse partition from path: {gcs_path}")
    
    return date_match.group(1), hour_match.group(1)
