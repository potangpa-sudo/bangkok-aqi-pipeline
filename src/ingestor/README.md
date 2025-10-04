# Bangkok AQI Ingestor Service

FastAPI service for ingesting Bangkok weather and air quality data from Open-Meteo API to Google Cloud Storage.

## Features

- ✅ Fetches weather and air quality data from Open-Meteo API
- ✅ Writes raw JSON to GCS with Hive-style partitioning (date=YYYY-MM-DD/hour=HH/)
- ✅ Publishes "landed" events to Pub/Sub for downstream processing
- ✅ Health check endpoint for Cloud Run
- ✅ Structured logging
- ✅ Dockerized for Cloud Run deployment

## Local Development

### Prerequisites

- Python 3.11+
- GCP credentials configured (`gcloud auth application-default login`)
- Environment variables set (see `.env.example`)

### Setup

```bash
cd src/ingestor
pip install -r requirements.txt
```

### Run Locally

```bash
# Set environment variables
export GCP_PROJECT_ID=your-project-id
export GCS_BUCKET_RAW=bangkok-aqi-raw
export GCS_BUCKET_QUAR=bangkok-aqi-quarantine
export PUBSUB_TOPIC=aqi-raw-landed
export TIMEZONE=Asia/Bangkok

# Start the service
python app.py
```

The service will be available at `http://localhost:8080`.

### Test Endpoints

```bash
# Health check
curl http://localhost:8080/healthz

# Ingest hourly data
curl -X POST "http://localhost:8080/ingest/hourly?city=Bangkok"

# Ingest with custom location
curl -X POST "http://localhost:8080/ingest/hourly?city=Bangkok&latitude=13.7563&longitude=100.5018"

# Backfill (ingest data from 3 hours ago)
curl -X POST "http://localhost:8080/ingest/hourly?hour_offset=-3"
```

## Docker Build

```bash
# Build image
docker build -t aqi-ingestor .

# Run locally
docker run -p 8080:8080 \
  -e GCP_PROJECT_ID=your-project-id \
  -e GCS_BUCKET_RAW=bangkok-aqi-raw \
  -e PUBSUB_TOPIC=aqi-raw-landed \
  -v ~/.config/gcloud:/root/.config/gcloud \
  aqi-ingestor
```

## Deploy to Cloud Run

### Option 1: Using gcloud CLI

```bash
# Set variables
export PROJECT_ID=your-project-id
export REGION=asia-southeast1
export SERVICE_NAME=aqi-ingestor

# Build and push to Container Registry
gcloud builds submit --tag gcr.io/${PROJECT_ID}/${SERVICE_NAME}

# Deploy to Cloud Run
gcloud run deploy ${SERVICE_NAME} \
  --image gcr.io/${PROJECT_ID}/${SERVICE_NAME} \
  --region ${REGION} \
  --platform managed \
  --service-account aqi-ingestor-sa@${PROJECT_ID}.iam.gserviceaccount.com \
  --set-env-vars "GCP_PROJECT_ID=${PROJECT_ID},GCS_BUCKET_RAW=bangkok-aqi-raw,PUBSUB_TOPIC=aqi-raw-landed,TIMEZONE=Asia/Bangkok" \
  --max-instances 10 \
  --min-instances 0 \
  --memory 512Mi \
  --cpu 1 \
  --timeout 300 \
  --allow-unauthenticated
```

### Option 2: Using Terraform

Deploy via Terraform (already configured in `/infra/terraform`):

```bash
cd infra/terraform
terraform apply
```

## API Documentation

Once deployed, access interactive API docs at:
- Swagger UI: `https://your-service-url/docs`
- ReDoc: `https://your-service-url/redoc`

## Monitoring

View logs in Cloud Logging:

```bash
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=${SERVICE_NAME}" \
  --limit 50 \
  --format json
```

## Architecture

```
┌─────────────┐
│ Cloud Run   │
│ (Ingestor)  │
└──────┬──────┘
       │
       ├──────> Open-Meteo API (fetch data)
       │
       ├──────> GCS (write raw JSON)
       │        └─ date=YYYY-MM-DD/hour=HH/*.json
       │
       └──────> Pub/Sub (publish event)
                └─ aqi-raw-landed topic
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GCP_PROJECT_ID` | GCP Project ID | - (required) |
| `GCP_REGION` | GCP Region | `asia-southeast1` |
| `GCS_BUCKET_RAW` | Raw data bucket name | - (required) |
| `GCS_BUCKET_QUAR` | Quarantine bucket name | - (required) |
| `PUBSUB_TOPIC` | Pub/Sub topic name | `aqi-raw-landed` |
| `OPEN_METEO_BASE` | Open-Meteo API base URL | `https://api.open-meteo.com/v1` |
| `TIMEZONE` | Timezone for data | `Asia/Bangkok` |
| `PORT` | Server port | `8080` |

## Testing

```bash
# Run tests (TODO)
pytest tests/
```

## Next Steps

1. Add unit tests for clients and utils
2. Add integration tests with mocked GCS/Pub/Sub
3. Implement retry logic with exponential backoff
4. Add metrics and custom logging
5. Implement request rate limiting
