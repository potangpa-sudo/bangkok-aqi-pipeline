# Bangkok AQI Spark Cleansing Job

PySpark job for cleansing and normalizing raw Bangkok AQI data from GCS to BigQuery.

## Overview

This Spark job:
1. Reads raw JSON files from GCS partitions (date=YYYY-MM-DD/hour=HH/)
2. Normalizes weather and air quality data into structured DataFrames
3. Validates data quality and quarantines bad records
4. Writes clean data to BigQuery staging tables with hourly partitioning
5. Uses MERGE semantics to avoid duplicates (idempotent)

## Local Testing

### Prerequisites

- Python 3.11+
- PySpark 3.4+
- GCP credentials configured

### Setup

```bash
pip install pyspark==3.4.1 google-cloud-storage google-cloud-bigquery
```

### Run Locally (against GCS)

```bash
spark-submit \
  --packages com.google.cloud.spark:spark-bigquery-with-dependencies_2.12:0.32.2 \
  spark/cleanse.py \
  --project_id your-project-id \
  --raw_bucket bangkok-aqi-raw \
  --quar_bucket bangkok-aqi-quarantine \
  --partition_date 2025-10-05 \
  --partition_hour 14
```

### Run with Sample Data

```bash
# Create sample data locally
mkdir -p data/raw/date=2025-10-05/hour=14/

# Run against local data (modify cleanse.py to use local paths for testing)
spark-submit spark/cleanse.py \
  --project_id your-project-id \
  --raw_bucket data/raw \
  --quar_bucket data/quarantine \
  --partition_date 2025-10-05 \
  --partition_hour 14
```

## Deploy to GCS

Upload Spark scripts to GCS bucket:

```bash
export RAW_BUCKET=bangkok-aqi-raw

# Upload main script
gsutil cp spark/cleanse.py gs://${RAW_BUCKET}/spark/

# Verify
gsutil ls gs://${RAW_BUCKET}/spark/
```

## Submit to Dataproc Serverless

### Via gcloud CLI

```bash
gcloud dataproc batches submit pyspark \
  gs://bangkok-aqi-raw/spark/cleanse.py \
  --project=your-project-id \
  --region=asia-southeast1 \
  --service-account=aqi-dataproc-sa@your-project-id.iam.gserviceaccount.com \
  --version=2.1 \
  --properties="spark.executor.instances=2,spark.driver.memory=2g,spark.executor.memory=2g" \
  -- \
  --project_id your-project-id \
  --raw_bucket bangkok-aqi-raw \
  --quar_bucket bangkok-aqi-quarantine \
  --partition_date 2025-10-05 \
  --partition_hour 14
```

### Via Airflow (Recommended)

The Airflow DAG (`airflow/dags/aqi_hourly.py`) automatically submits this job with proper parameters.

## Schema

### Input (Raw JSON from Open-Meteo)

**Weather**:
```json
{
  "latitude": 13.7563,
  "longitude": 100.5018,
  "hourly": {
    "time": ["2025-10-05T14:00", "2025-10-05T15:00"],
    "temperature_2m": [28.5, 29.1],
    "relative_humidity_2m": [75.0, 73.5],
    ...
  }
}
```

**Air Quality**:
```json
{
  "latitude": 13.7563,
  "longitude": 100.5018,
  "hourly": {
    "time": ["2025-10-05T14:00", "2025-10-05T15:00"],
    "pm10": [45.2, 42.8],
    "pm2_5": [28.5, 26.1],
    "us_aqi": [85, 78],
    ...
  }
}
```

### Output (BigQuery Staging Tables)

**staging_aqi.weather_hourly**:
- `event_hour` (TIMESTAMP, partition key)
- `latitude` (FLOAT64)
- `longitude` (FLOAT64)
- `temperature_2m` (FLOAT64)
- `relative_humidity_2m` (FLOAT64)
- `precipitation` (FLOAT64)
- `wind_speed_10m` (FLOAT64)
- `wind_direction_10m` (FLOAT64)
- `source` (STRING, cluster key)
- `ingested_at` (TIMESTAMP)

**staging_aqi.aqi_hourly**:
- `event_hour` (TIMESTAMP, partition key)
- `latitude` (FLOAT64)
- `longitude` (FLOAT64)
- `pm10` (FLOAT64)
- `pm2_5` (FLOAT64)
- `carbon_monoxide` (FLOAT64)
- `nitrogen_dioxide` (FLOAT64)
- `sulphur_dioxide` (FLOAT64)
- `ozone` (FLOAT64)
- `us_aqi` (INT64)
- `european_aqi` (INT64)
- `source` (STRING, cluster key)
- `ingested_at` (TIMESTAMP)

## Error Handling

- **Missing data**: Logs warning and continues
- **Bad records**: Quarantined to `gs://bangkok-aqi-quarantine/date=.../hour=.../bad/*.json`
- **Schema mismatch**: Job fails with detailed error message
- **BigQuery write failure**: Job fails and can be retried (idempotent)

## Monitoring

View Dataproc batch job logs:

```bash
gcloud dataproc batches list --region=asia-southeast1

gcloud dataproc batches describe BATCH_ID --region=asia-southeast1
```

Query BigQuery for results:

```sql
SELECT COUNT(*) as row_count, event_hour
FROM `your-project-id.staging_aqi.weather_hourly`
WHERE DATE(event_hour) = '2025-10-05'
GROUP BY event_hour
ORDER BY event_hour;
```

## Cost Optimization

- Uses Dataproc Serverless (pay per second, no cluster overhead)
- Dynamic allocation enabled (scales executors based on workload)
- Partition pruning in BigQuery (only reads/writes relevant hours)
- Clustering by `source` for efficient queries

## Next Steps

1. Add unit tests with pytest and mocked Spark session
2. Implement incremental processing (only new partitions)
3. Add data lineage tracking
4. Implement SLA monitoring (data freshness alerts)
