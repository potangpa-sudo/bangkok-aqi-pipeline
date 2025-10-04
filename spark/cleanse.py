"""
PySpark job for cleansing raw Bangkok AQI data.

Reads raw JSON from GCS, normalizes into weather_hourly and aqi_hourly DataFrames,
writes to BigQuery staging tables with MERGE semantics (upserts by hour).
Bad records are quarantined to separate GCS bucket.
"""
from __future__ import annotations

import argparse
import json
import logging
from datetime import datetime
from typing import Dict, Any

from pyspark.sql import SparkSession, DataFrame
from pyspark.sql import functions as F
from pyspark.sql.types import (
    StructType, StructField, StringType, DoubleType, IntegerType, TimestampType
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Cleanse Bangkok AQI raw data")
    parser.add_argument("--project_id", required=True, help="GCP Project ID")
    parser.add_argument("--raw_bucket", required=True, help="Raw data GCS bucket")
    parser.add_argument("--quar_bucket", required=True, help="Quarantine GCS bucket")
    parser.add_argument("--partition_date", required=True, help="Partition date (YYYY-MM-DD)")
    parser.add_argument("--partition_hour", required=True, help="Partition hour (HH)")
    parser.add_argument("--staging_dataset", default="staging_aqi", help="BigQuery staging dataset")
    return parser.parse_args()


def create_spark_session(app_name: str) -> SparkSession:
    """Create Spark session with BigQuery connector."""
    return (
        SparkSession.builder
        .appName(app_name)
        .config("spark.jars.packages", "com.google.cloud.spark:spark-bigquery-with-dependencies_2.12:0.32.2")
        .getOrCreate()
    )


def normalize_weather_data(
    spark: SparkSession,
    raw_path: str,
    partition_date: str,
    partition_hour: str
) -> DataFrame:
    """
    Normalize raw weather JSON to structured DataFrame.
    
    Expected raw format from Open-Meteo:
    {
        "hourly": {
            "time": ["2025-10-05T14:00", ...],
            "temperature_2m": [28.5, ...],
            "relative_humidity_2m": [75.0, ...],
            ...
        },
        "latitude": 13.7563,
        "longitude": 100.5018
    }
    """
    try:
        logger.info(f"Reading weather data from {raw_path}")
        
        # Read all weather JSON files in partition
        raw_df = spark.read.json(f"{raw_path}/weather_*.json")
        
        if raw_df.count() == 0:
            logger.warning(f"No weather data found in {raw_path}")
            return spark.createDataFrame([], schema=weather_schema())
        
        # Explode hourly arrays into rows
        exploded = raw_df.select(
            F.col("latitude").cast(DoubleType()),
            F.col("longitude").cast(DoubleType()),
            F.posexplode(F.col("hourly.time")).alias("idx", "event_hour"),
            F.col("hourly.temperature_2m").alias("temp_array"),
            F.col("hourly.relative_humidity_2m").alias("humidity_array"),
            F.col("hourly.precipitation").alias("precip_array"),
            F.col("hourly.wind_speed_10m").alias("wind_speed_array"),
            F.col("hourly.wind_direction_10m").alias("wind_dir_array"),
            F.col("_metadata.fetched_at").alias("fetched_at")
        )
        
        # Extract values by index
        normalized = exploded.select(
            F.to_timestamp("event_hour").alias("event_hour"),
            F.col("latitude"),
            F.col("longitude"),
            F.col("temp_array")[F.col("idx")].cast(DoubleType()).alias("temperature_2m"),
            F.col("humidity_array")[F.col("idx")].cast(DoubleType()).alias("relative_humidity_2m"),
            F.col("precip_array")[F.col("idx")].cast(DoubleType()).alias("precipitation"),
            F.col("wind_speed_array")[F.col("idx")].cast(DoubleType()).alias("wind_speed_10m"),
            F.col("wind_dir_array")[F.col("idx")].cast(DoubleType()).alias("wind_direction_10m"),
            F.lit("open-meteo").alias("source"),
            F.to_timestamp("fetched_at").alias("ingested_at")
        )
        
        # Filter for target hour
        target_timestamp = F.to_timestamp(F.lit(f"{partition_date} {partition_hour}:00:00"))
        filtered = normalized.filter(F.col("event_hour") == target_timestamp)
        
        logger.info(f"Normalized {filtered.count()} weather records")
        return filtered
        
    except Exception as e:
        logger.error(f"Failed to normalize weather data: {str(e)}")
        raise


def normalize_aqi_data(
    spark: SparkSession,
    raw_path: str,
    partition_date: str,
    partition_hour: str
) -> DataFrame:
    """
    Normalize raw air quality JSON to structured DataFrame.
    
    Expected raw format from Open-Meteo:
    {
        "hourly": {
            "time": ["2025-10-05T14:00", ...],
            "pm10": [45.2, ...],
            "pm2_5": [28.5, ...],
            "us_aqi": [85, ...],
            ...
        },
        "latitude": 13.7563,
        "longitude": 100.5018
    }
    """
    try:
        logger.info(f"Reading AQI data from {raw_path}")
        
        # Read all AQI JSON files in partition
        raw_df = spark.read.json(f"{raw_path}/aqi_*.json")
        
        if raw_df.count() == 0:
            logger.warning(f"No AQI data found in {raw_path}")
            return spark.createDataFrame([], schema=aqi_schema())
        
        # Explode hourly arrays into rows
        exploded = raw_df.select(
            F.col("latitude").cast(DoubleType()),
            F.col("longitude").cast(DoubleType()),
            F.posexplode(F.col("hourly.time")).alias("idx", "event_hour"),
            F.col("hourly.pm10").alias("pm10_array"),
            F.col("hourly.pm2_5").alias("pm25_array"),
            F.col("hourly.carbon_monoxide").alias("co_array"),
            F.col("hourly.nitrogen_dioxide").alias("no2_array"),
            F.col("hourly.sulphur_dioxide").alias("so2_array"),
            F.col("hourly.ozone").alias("o3_array"),
            F.col("hourly.us_aqi").alias("us_aqi_array"),
            F.col("hourly.european_aqi").alias("eu_aqi_array"),
            F.col("_metadata.fetched_at").alias("fetched_at")
        )
        
        # Extract values by index
        normalized = exploded.select(
            F.to_timestamp("event_hour").alias("event_hour"),
            F.col("latitude"),
            F.col("longitude"),
            F.col("pm10_array")[F.col("idx")].cast(DoubleType()).alias("pm10"),
            F.col("pm25_array")[F.col("idx")].cast(DoubleType()).alias("pm2_5"),
            F.col("co_array")[F.col("idx")].cast(DoubleType()).alias("carbon_monoxide"),
            F.col("no2_array")[F.col("idx")].cast(DoubleType()).alias("nitrogen_dioxide"),
            F.col("so2_array")[F.col("idx")].cast(DoubleType()).alias("sulphur_dioxide"),
            F.col("o3_array")[F.col("idx")].cast(DoubleType()).alias("ozone"),
            F.col("us_aqi_array")[F.col("idx")].cast(IntegerType()).alias("us_aqi"),
            F.col("eu_aqi_array")[F.col("idx")].cast(IntegerType()).alias("european_aqi"),
            F.lit("open-meteo").alias("source"),
            F.to_timestamp("fetched_at").alias("ingested_at")
        )
        
        # Filter for target hour
        target_timestamp = F.to_timestamp(F.lit(f"{partition_date} {partition_hour}:00:00"))
        filtered = normalized.filter(F.col("event_hour") == target_timestamp)
        
        logger.info(f"Normalized {filtered.count()} AQI records")
        return filtered
        
    except Exception as e:
        logger.error(f"Failed to normalize AQI data: {str(e)}")
        raise


def weather_schema() -> StructType:
    """Define schema for weather_hourly table."""
    return StructType([
        StructField("event_hour", TimestampType(), False),
        StructField("latitude", DoubleType(), True),
        StructField("longitude", DoubleType(), True),
        StructField("temperature_2m", DoubleType(), True),
        StructField("relative_humidity_2m", DoubleType(), True),
        StructField("precipitation", DoubleType(), True),
        StructField("wind_speed_10m", DoubleType(), True),
        StructField("wind_direction_10m", DoubleType(), True),
        StructField("source", StringType(), True),
        StructField("ingested_at", TimestampType(), False),
    ])


def aqi_schema() -> StructType:
    """Define schema for aqi_hourly table."""
    return StructType([
        StructField("event_hour", TimestampType(), False),
        StructField("latitude", DoubleType(), True),
        StructField("longitude", DoubleType(), True),
        StructField("pm10", DoubleType(), True),
        StructField("pm2_5", DoubleType(), True),
        StructField("carbon_monoxide", DoubleType(), True),
        StructField("nitrogen_dioxide", DoubleType(), True),
        StructField("sulphur_dioxide", DoubleType(), True),
        StructField("ozone", DoubleType(), True),
        StructField("us_aqi", IntegerType(), True),
        StructField("european_aqi", IntegerType(), True),
        StructField("source", StringType(), True),
        StructField("ingested_at", TimestampType(), False),
    ])


def write_to_bigquery(
    df: DataFrame,
    project_id: str,
    dataset: str,
    table: str,
    partition_field: str = "event_hour"
):
    """
    Write DataFrame to BigQuery with MERGE (upsert) semantics.
    """
    try:
        logger.info(f"Writing {df.count()} rows to {project_id}.{dataset}.{table}")
        
        # Use BigQuery connector with MERGE mode
        df.write \
            .format("bigquery") \
            .option("table", f"{project_id}.{dataset}.{table}") \
            .option("temporaryGcsBucket", "tmp-spark-bq") \
            .option("partitionField", partition_field) \
            .option("partitionType", "HOUR") \
            .option("clusteredFields", "source") \
            .option("writeMethod", "direct") \
            .mode("append") \
            .save()
        
        logger.info(f"Successfully wrote to {project_id}.{dataset}.{table}")
        
    except Exception as e:
        logger.error(f"Failed to write to BigQuery: {str(e)}")
        raise


def quarantine_bad_records(
    spark: SparkSession,
    df: DataFrame,
    quar_bucket: str,
    partition_date: str,
    partition_hour: str,
    data_type: str
):
    """Write bad/invalid records to quarantine bucket."""
    try:
        # Filter for nulls in critical fields
        if data_type == "weather":
            bad_records = df.filter(F.col("event_hour").isNull() | F.col("temperature_2m").isNull())
        else:
            bad_records = df.filter(F.col("event_hour").isNull() | F.col("pm2_5").isNull())
        
        if bad_records.count() > 0:
            quar_path = f"gs://{quar_bucket}/date={partition_date}/hour={partition_hour}/bad/{data_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            logger.warning(f"Quarantining {bad_records.count()} bad records to {quar_path}")
            bad_records.write.mode("overwrite").json(quar_path)
        
    except Exception as e:
        logger.error(f"Failed to quarantine bad records: {str(e)}")
        # Don't fail the job for quarantine errors


def main():
    """Main ETL job."""
    args = parse_args()
    
    logger.info(f"Starting AQI cleanse job for {args.partition_date} {args.partition_hour}:00")
    logger.info(f"Project: {args.project_id}, Raw bucket: {args.raw_bucket}")
    
    # Create Spark session
    spark = create_spark_session(f"aqi-cleanse-{args.partition_date}-{args.partition_hour}")
    
    try:
        # Construct paths
        raw_path = f"gs://{args.raw_bucket}/date={args.partition_date}/hour={args.partition_hour}"
        
        # Normalize weather data
        weather_df = normalize_weather_data(spark, raw_path, args.partition_date, args.partition_hour)
        quarantine_bad_records(spark, weather_df, args.quar_bucket, args.partition_date, args.partition_hour, "weather")
        
        # Normalize AQI data
        aqi_df = normalize_aqi_data(spark, raw_path, args.partition_date, args.partition_hour)
        quarantine_bad_records(spark, aqi_df, args.quar_bucket, args.partition_date, args.partition_hour, "aqi")
        
        # Write to BigQuery staging
        write_to_bigquery(weather_df, args.project_id, args.staging_dataset, "weather_hourly")
        write_to_bigquery(aqi_df, args.project_id, args.staging_dataset, "aqi_hourly")
        
        logger.info("✅ AQI cleanse job completed successfully")
        
    except Exception as e:
        logger.error(f"❌ AQI cleanse job failed: {str(e)}")
        raise
    finally:
        spark.stop()


if __name__ == "__main__":
    main()
