"""
FastAPI application for ingesting Bangkok weather and air quality data.
Writes raw JSON to GCS and publishes events to Pub/Sub.
"""
from __future__ import annotations

import logging
import os
from datetime import datetime, timezone
from typing import Dict, Any

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
import uvicorn

from .clients import GCSClient, PubSubClient
from .schemas import IngestionRequest, IngestionResponse
from .utils import get_partition_path, fetch_open_meteo_data

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Bangkok AQI Ingestor",
    description="Ingest weather and air quality data to GCS",
    version="1.0.0"
)

# Initialize clients
gcs_client = GCSClient()
pubsub_client = PubSubClient()

# Environment variables
PROJECT_ID = os.getenv("GCP_PROJECT_ID")
REGION = os.getenv("GCP_REGION", "asia-southeast1")
RAW_BUCKET = os.getenv("GCS_BUCKET_RAW")
PUBSUB_TOPIC = os.getenv("PUBSUB_TOPIC")
OPEN_METEO_BASE = os.getenv("OPEN_METEO_BASE", "https://api.open-meteo.com/v1")
TIMEZONE = os.getenv("TIMEZONE", "Asia/Bangkok")


@app.get("/healthz")
async def health_check() -> Dict[str, str]:
    """Health check endpoint for Cloud Run."""
    return {"status": "healthy", "service": "aqi-ingestor"}


@app.get("/")
async def root() -> Dict[str, str]:
    """Root endpoint with API info."""
    return {
        "service": "Bangkok AQI Ingestor",
        "version": "1.0.0",
        "endpoints": {
            "health": "/healthz",
            "ingest_hourly": "/ingest/hourly?city=Bangkok",
        }
    }


@app.post("/ingest/hourly")
async def ingest_hourly(
    city: str = Query("Bangkok", description="City name for logging"),
    latitude: float = Query(13.7563, description="Latitude"),
    longitude: float = Query(100.5018, description="Longitude"),
    hour_offset: int = Query(0, description="Hours to offset from current time"),
) -> IngestionResponse:
    """
    Ingest hourly weather and air quality data for a location.
    
    - Fetches data from Open-Meteo API
    - Writes raw JSON to GCS with partition structure: date=YYYY-MM-DD/hour=HH/
    - Publishes event to Pub/Sub topic
    
    Args:
        city: City name for logging and metadata
        latitude: Location latitude
        longitude: Location longitude
        hour_offset: Hours to offset from current UTC time (for backfills)
    
    Returns:
        IngestionResponse with status and details
    """
    try:
        logger.info(f"Starting ingestion for {city} (lat={latitude}, lon={longitude})")
        
        # Calculate target hour
        now = datetime.now(timezone.utc)
        if hour_offset != 0:
            from datetime import timedelta
            now = now + timedelta(hours=hour_offset)
        
        # Get partition path
        date_str, hour_str = get_partition_path(now)
        
        # Fetch weather data
        logger.info("Fetching weather data...")
        weather_data = fetch_open_meteo_data(
            base_url=OPEN_METEO_BASE,
            endpoint="forecast",
            latitude=latitude,
            longitude=longitude,
            timezone=TIMEZONE,
            data_type="weather"
        )
        
        # Fetch air quality data
        logger.info("Fetching air quality data...")
        aqi_data = fetch_open_meteo_data(
            base_url=OPEN_METEO_BASE,
            endpoint="air-quality",
            latitude=latitude,
            longitude=longitude,
            timezone=TIMEZONE,
            data_type="air_quality"
        )
        
        # Write to GCS
        weather_path = f"date={date_str}/hour={hour_str}/weather_{now.strftime('%Y%m%d_%H%M%S')}.json"
        aqi_path = f"date={date_str}/hour={hour_str}/aqi_{now.strftime('%Y%m%d_%H%M%S')}.json"
        
        logger.info(f"Writing weather data to gs://{RAW_BUCKET}/{weather_path}")
        gcs_client.write_json(RAW_BUCKET, weather_path, weather_data)
        
        logger.info(f"Writing AQI data to gs://{RAW_BUCKET}/{aqi_path}")
        gcs_client.write_json(RAW_BUCKET, aqi_path, aqi_data)
        
        # Publish to Pub/Sub
        event_data = {
            "city": city,
            "date": date_str,
            "hour": hour_str,
            "weather_path": f"gs://{RAW_BUCKET}/{weather_path}",
            "aqi_path": f"gs://{RAW_BUCKET}/{aqi_path}",
            "ingested_at": now.isoformat(),
        }
        
        logger.info(f"Publishing event to {PUBSUB_TOPIC}")
        message_id = pubsub_client.publish_message(
            project_id=PROJECT_ID,
            topic_name=PUBSUB_TOPIC,
            data=event_data
        )
        
        logger.info(f"Ingestion complete. Message ID: {message_id}")
        
        return IngestionResponse(
            status="success",
            message=f"Data ingested for {city} at {date_str} {hour_str}:00",
            details={
                "date": date_str,
                "hour": hour_str,
                "weather_path": weather_path,
                "aqi_path": aqi_path,
                "pubsub_message_id": message_id,
            }
        )
        
    except Exception as e:
        logger.error(f"Ingestion failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8080"))
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
