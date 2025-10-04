# Bangkok AQI Pipeline - Deployment Guide

This guide walks through deploying the entire Bangkok AQI pipeline from scratch.

## Prerequisites Checklist

- [ ] GCP Project created with billing enabled
- [ ] `gcloud` CLI installed and authenticated
- [ ] Terraform >= 1.5.0 installed
- [ ] Docker installed (for building images)
- [ ] Python 3.11+ installed
- [ ] Git repository cloned locally

## Phase 1: Initial Setup (30 minutes)

### 1.1 Configure GCP Project

```bash
# Set your project ID
export PROJECT_ID="your-project-id"

# Authenticate gcloud
gcloud auth login
gcloud auth application-default login

# Set default project
gcloud config set project ${PROJECT_ID}

# Enable required APIs (Terraform will also do this)
gcloud services enable \
  storage.googleapis.com \
  bigquery.googleapis.com \
  pubsub.googleapis.com \
  run.googleapis.com \
  composer.googleapis.com \
  dataproc.googleapis.com \
  secretmanager.googleapis.com \
  compute.googleapis.com \
  servicenetworking.googleapis.com
```

### 1.2 Configure Environment Variables

```bash
# Copy example environment file
cp .env.example .env

# Edit with your values
nano .env
```

Required variables:
- `GCP_PROJECT_ID`: Your GCP project ID
- `GCS_BUCKET_RAW`: Unique bucket name for raw data (e.g., `yourproject-aqi-raw`)
- `GCS_BUCKET_QUAR`: Unique bucket name for quarantine (e.g., `yourproject-aqi-quarantine`)

### 1.3 Create Terraform Variables File

```bash
cd infra/terraform
cp terraform.tfvars.example terraform.tfvars
nano terraform.tfvars
```

Update all placeholder values with your actual project details.

## Phase 2: Infrastructure Deployment (20 minutes)

### 2.1 Initialize Terraform

```bash
cd infra/terraform

# Initialize
terraform init

# Validate configuration
terraform validate

# Format code
terraform fmt -recursive
```

### 2.2 Review Infrastructure Plan

```bash
# Generate plan
terraform plan -out=tfplan

# Review outputs (important!)
# Look for:
# - Service account emails
# - Bucket names
# - BigQuery dataset IDs
# - Cloud Run URLs (will be empty initially)
```

### 2.3 Deploy Infrastructure

```bash
# Apply plan
terraform apply tfplan

# Save outputs for later use
terraform output -json > ../../outputs.json

# Extract key values
export RAW_BUCKET=$(terraform output -raw gcs_bucket_raw_name)
export QUAR_BUCKET=$(terraform output -raw gcs_bucket_quarantine_name)
export COMPOSER_BUCKET=$(terraform output -raw composer_gcs_bucket)
export INGESTOR_SA=$(terraform output -raw ingestor_sa_email)
export DATAPROC_SA=$(terraform output -raw dataproc_sa_email)
```

⏱️ **Note**: Cloud Composer environment takes ~20-30 minutes to create.

### 2.4 Verify Infrastructure

```bash
# Check GCS buckets
gsutil ls

# Check BigQuery datasets
bq ls

# Check service accounts
gcloud iam service-accounts list

# Check Pub/Sub topics
gcloud pubsub topics list
```

## Phase 3: Application Deployment (30 minutes)

### 3.1 Build and Deploy Ingestor Service

```bash
cd ../../src/ingestor

# Build image
gcloud builds submit --tag gcr.io/${PROJECT_ID}/aqi-ingestor:latest

# Deploy to Cloud Run
gcloud run deploy aqi-ingestor \
  --image gcr.io/${PROJECT_ID}/aqi-ingestor:latest \
  --region asia-southeast1 \
  --platform managed \
  --service-account ${INGESTOR_SA} \
  --set-env-vars "GCP_PROJECT_ID=${PROJECT_ID},GCS_BUCKET_RAW=${RAW_BUCKET},GCS_BUCKET_QUAR=${QUAR_BUCKET},PUBSUB_TOPIC=aqi-raw-landed,TIMEZONE=Asia/Bangkok" \
  --max-instances 10 \
  --min-instances 0 \
  --memory 512Mi \
  --cpu 1 \
  --timeout 300 \
  --allow-unauthenticated

# Get service URL
export INGESTOR_URL=$(gcloud run services describe aqi-ingestor --region asia-southeast1 --format='value(status.url)')
echo "Ingestor URL: ${INGESTOR_URL}"

# Test health endpoint
curl ${INGESTOR_URL}/healthz
```

### 3.2 Build and Deploy Dashboard Service

```bash
cd ../../app

# Build image
gcloud builds submit --tag gcr.io/${PROJECT_ID}/aqi-dashboard:latest

# Deploy to Cloud Run
gcloud run deploy aqi-dashboard \
  --image gcr.io/${PROJECT_ID}/aqi-dashboard:latest \
  --region asia-southeast1 \
  --platform managed \
  --service-account ${INGESTOR_SA} \
  --set-env-vars "GCP_PROJECT_ID=${PROJECT_ID},BQ_DATASET_MARTS=marts_aqi,MODE=bigquery" \
  --max-instances 5 \
  --min-instances 0 \
  --memory 512Mi \
  --cpu 1 \
  --timeout 300 \
  --allow-unauthenticated

# Get service URL
export DASHBOARD_URL=$(gcloud run services describe aqi-dashboard --region asia-southeast1 --format='value(status.url)')
echo "Dashboard URL: ${DASHBOARD_URL}"
```

### 3.3 Upload Spark Job to GCS

```bash
cd ../spark

# Upload Spark script
gsutil cp cleanse.py gs://${RAW_BUCKET}/spark/

# Upload config
gsutil cp job_config.json gs://${RAW_BUCKET}/spark/

# Verify
gsutil ls gs://${RAW_BUCKET}/spark/
```

### 3.4 Deploy Airflow DAG

```bash
cd ../airflow/dags

# Wait for Composer to finish creating (if still in progress)
gcloud composer environments list --locations asia-southeast1

# Upload DAG
gcloud composer environments storage dags import \
  --environment bangkok-aqi-composer \
  --location asia-southeast1 \
  --source aqi_hourly.py

# Verify upload
gcloud composer environments storage dags list \
  --environment bangkok-aqi-composer \
  --location asia-southeast1
```

## Phase 4: Initial Data Load (15 minutes)

### 4.1 Manual Ingestion Test

```bash
# Trigger ingestion for current hour
curl -X POST "${INGESTOR_URL}/ingest/hourly?city=Bangkok"

# Check GCS for raw files
gsutil ls gs://${RAW_BUCKET}/date=$(date +%Y-%m-%d)/hour=$(date +%H)/

# Check Pub/Sub for messages
gcloud pubsub subscriptions pull aqi-raw-landed-sub --limit=1
```

### 4.2 Run Spark Cleanse Job Manually

```bash
# Get current date and hour
CURRENT_DATE=$(date +%Y-%m-%d)
CURRENT_HOUR=$(date +%H)

# Submit Dataproc batch job
gcloud dataproc batches submit pyspark \
  gs://${RAW_BUCKET}/spark/cleanse.py \
  --project=${PROJECT_ID} \
  --region=asia-southeast1 \
  --service-account=${DATAPROC_SA} \
  --version=2.1 \
  --properties="spark.executor.instances=2,spark.driver.memory=2g,spark.executor.memory=2g" \
  -- \
  --project_id ${PROJECT_ID} \
  --raw_bucket ${RAW_BUCKET} \
  --quar_bucket ${QUAR_BUCKET} \
  --partition_date ${CURRENT_DATE} \
  --partition_hour ${CURRENT_HOUR}

# Monitor job
gcloud dataproc batches list --region=asia-southeast1
```

### 4.3 Run dbt Models

```bash
cd ../../dbt

# Install dbt
pip install -r requirements.txt

# Set environment variables
export GCP_PROJECT_ID=${PROJECT_ID}
export DBT_SERVICE_ACCOUNT_PATH=/path/to/service-account-key.json

# Compile models (dry run)
dbt compile --profiles-dir . --target prod

# Run models
dbt run --profiles-dir . --target prod

# Run tests
dbt test --profiles-dir . --target prod

# Generate docs
dbt docs generate
```

### 4.4 Verify Data in BigQuery

```bash
# Query staging tables
bq query --nouse_legacy_sql \
  'SELECT COUNT(*) as row_count, MAX(event_hour) as latest_hour
   FROM `'${PROJECT_ID}'.staging_aqi.weather_hourly`'

bq query --nouse_legacy_sql \
  'SELECT COUNT(*) as row_count, MAX(event_hour) as latest_hour
   FROM `'${PROJECT_ID}'.staging_aqi.aqi_hourly`'

# Query marts tables
bq query --nouse_legacy_sql \
  'SELECT * FROM `'${PROJECT_ID}'.marts_aqi.mart_daily_aqi_weather`
   ORDER BY date DESC LIMIT 5'
```

### 4.5 View Dashboard

```bash
# Open dashboard in browser
open ${DASHBOARD_URL}

# Or use curl to test
curl ${DASHBOARD_URL}/_stcore/health
```

## Phase 5: Enable Airflow Orchestration (10 minutes)

### 5.1 Access Airflow UI

```bash
# Get Airflow web UI URL
export AIRFLOW_URL=$(gcloud composer environments describe bangkok-aqi-composer \
  --location asia-southeast1 \
  --format='value(config.airflowUri)')

echo "Airflow URL: ${AIRFLOW_URL}"

# Open in browser
open ${AIRFLOW_URL}
```

### 5.2 Enable and Trigger DAG

In Airflow UI:
1. Navigate to DAGs page
2. Find `aqi_hourly_pipeline`
3. Toggle to **ON**
4. Click **Trigger DAG** button
5. Monitor execution in Graph/Tree view

### 5.3 Verify Airflow Variables

In Airflow UI → Admin → Variables:
- Add `GCP_PROJECT_ID` = your project ID
- Add `GCS_BUCKET_RAW` = your raw bucket name
- Add `INGESTOR_SERVICE_URL` = your ingestor URL

## Phase 6: Setup CI/CD (15 minutes)

### 6.1 Configure GitHub Secrets

In GitHub repository → Settings → Secrets and variables → Actions:

Add the following secrets:
- `GCP_PROJECT_ID`: Your GCP project ID
- `GCP_SA_KEY`: Service account JSON key for deployment
- `GCS_BUCKET_RAW`: Raw data bucket name
- `GCS_BUCKET_QUAR`: Quarantine bucket name

### 6.2 Test CI Pipeline

```bash
# Create a feature branch
git checkout -b test-ci

# Make a small change
echo "# Test" >> README.md

# Commit and push
git add README.md
git commit -m "test: trigger CI pipeline"
git push origin test-ci

# Open PR and watch CI run
```

### 6.3 Test Deployment Pipeline

Merge the PR to `main` and watch the deployment pipeline run.

## Phase 7: Monitoring Setup (10 minutes)

### 7.1 Create Cloud Monitoring Dashboard

```bash
# Create a simple uptime check
gcloud monitoring uptime-checks create ${INGESTOR_URL}/healthz \
  --display-name="AQI Ingestor Health" \
  --period=60s

# Create alerting policy
gcloud alpha monitoring policies create \
  --notification-channels=YOUR_CHANNEL_ID \
  --display-name="AQI Pipeline Alerts" \
  --condition-display-name="Ingestor Down" \
  --condition-threshold-value=1 \
  --condition-threshold-duration=300s
```

### 7.2 Setup Log-based Metrics

In Cloud Console → Logging → Logs Explorer:
1. Create log-based metric for pipeline failures
2. Create alert on metric threshold

### 7.3 Configure Slack Notifications (Optional)

```bash
# Store Slack webhook in Secret Manager
echo "https://hooks.slack.com/services/YOUR/WEBHOOK/URL" | \
  gcloud secrets versions add aqi-slack-webhook --data-file=-

# Update Airflow variables with webhook connection
```

## Phase 8: Testing & Validation (20 minutes)

### 8.1 End-to-End Test

```bash
# Trigger full pipeline
curl -X POST "${INGESTOR_URL}/ingest/hourly?city=Bangkok"

# Wait 5 minutes, then check Airflow DAG run
# Check BigQuery for new data
# Check dashboard for updated metrics
```

### 8.2 Failure Testing

```bash
# Test with bad data (should quarantine)
# Monitor error logs in Cloud Logging
# Verify alerting works
```

### 8.3 Performance Testing

```bash
# Trigger multiple ingestions in parallel
for i in {1..10}; do
  curl -X POST "${INGESTOR_URL}/ingest/hourly?city=Bangkok&hour_offset=-$i" &
done
wait

# Monitor Cloud Run metrics for scaling
# Monitor BigQuery query performance
```

## Troubleshooting

### Terraform Issues

**Error: Bucket already exists**
```bash
# Terraform doesn't import existing resources
# Either delete the bucket or import it
terraform import module.storage.google_storage_bucket.raw your-bucket-name
```

**Error: Service account not found**
```bash
# Wait a few seconds for IAM propagation
sleep 30
terraform apply
```

### Cloud Run Issues

**Error: Container failed to start**
```bash
# Check logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=aqi-ingestor" --limit 50

# Common issues:
# - Missing environment variables
# - Port not exposed correctly (should be 8080)
# - Application crash on startup
```

### Airflow Issues

**DAG not appearing**
```bash
# Check DAG parsing errors
gcloud composer environments run bangkok-aqi-composer \
  --location asia-southeast1 \
  list_dag_errors

# Check DAG file exists
gsutil ls gs://${COMPOSER_BUCKET}/dags/
```

### BigQuery Issues

**Error: Table not found**
```bash
# Check if Spark job ran successfully
gcloud dataproc batches list --region=asia-southeast1

# Check if dbt ran successfully
cd dbt && dbt run --profiles-dir . --target prod
```

## Post-Deployment Checklist

- [ ] All services deployed successfully
- [ ] Airflow DAG running hourly
- [ ] Data flowing end-to-end
- [ ] Dashboard accessible and showing data
- [ ] Monitoring alerts configured
- [ ] CI/CD pipelines working
- [ ] Documentation updated
- [ ] Team trained on operations

## Next Steps

1. **Backfill historical data** (if needed)
2. **Tune Spark job performance** (adjust executors, memory)
3. **Optimize BigQuery costs** (check query patterns)
4. **Add more comprehensive monitoring**
5. **Implement additional data quality checks**
6. **Plan for disaster recovery testing**

## Cleanup (If Needed)

To tear down the entire infrastructure:

```bash
cd infra/terraform

# Destroy all resources (⚠️ IRREVERSIBLE)
terraform destroy

# Or use GCP Console to delete resources manually
```

---

**Estimated Total Deployment Time: 2-3 hours**

For support, refer to:
- [Architecture Documentation](../docs/architecture.md)
- [Terraform README](../infra/terraform/README.md)
- [Individual service READMEs](../src/ingestor/README.md)
