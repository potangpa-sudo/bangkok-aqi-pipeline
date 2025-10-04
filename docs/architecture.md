# Bangkok AQI Pipeline - Architecture Documentation

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           BANGKOK AQI PIPELINE (GCP)                         │
└─────────────────────────────────────────────────────────────────────────────┘

┌──────────────┐
│ External API │
│ Open-Meteo   │
└──────┬───────┘
       │
       │ HTTP GET (hourly)
       ▼
┌──────────────────────┐
│   CLOUD RUN          │
│   aqi-ingestor       │◄─── Cloud Scheduler (hourly trigger)
│   (FastAPI)          │◄─── Manual trigger via HTTP
└─────┬────────────────┘
      │
      ├─────────► GCS (Raw Data)
      │           gs://bangkok-aqi-raw/
      │           └─ date=YYYY-MM-DD/hour=HH/*.json
      │
      └─────────► Pub/Sub Topic
                  aqi-raw-landed
                         │
                         ▼
                  ┌──────────────┐
                  │ CLOUD        │
                  │ COMPOSER     │
                  │ (Airflow)    │
                  └──────┬───────┘
                         │
           ┌─────────────┼─────────────┐
           │             │             │
           ▼             ▼             ▼
    ┌──────────┐  ┌──────────────┐  ┌─────────┐
    │  GCS     │  │  DATAPROC    │  │  dbt    │
    │  Sensor  │  │  SERVERLESS  │  │  (BQ)   │
    │          │  │  (PySpark)   │  │         │
    └──────────┘  └──────┬───────┘  └───┬─────┘
                         │              │
                         ▼              ▼
                  ┌──────────────────────────┐
                  │     BIGQUERY             │
                  ├──────────────────────────┤
                  │  staging_aqi             │
                  │  ├─ weather_hourly       │
                  │  └─ aqi_hourly           │
                  │                          │
                  │  marts_aqi               │
                  │  ├─ dim_datetime         │
                  │  ├─ fact_aqi_hourly      │
                  │  └─ mart_daily_aqi...    │
                  └────────┬─────────────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │  CLOUD RUN      │
                  │  aqi-dashboard  │
                  │  (Streamlit)    │
                  └─────────────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │  End Users      │
                  │  (Web Browser)  │
                  └─────────────────┘

         ┌──────────────────┐
         │  BAD RECORDS     │
         │  gs://bangkok-   │
         │  aqi-quarantine/ │
         └──────────────────┘
```

## Data Flow

### 1. **Ingestion** (Hourly)
- **Trigger**: Cloud Scheduler → Cloud Run (or Airflow HTTP Operator)
- **Process**:
  1. Fetch weather + air quality data from Open-Meteo API
  2. Write raw JSON to GCS with Hive partitioning: `date=YYYY-MM-DD/hour=HH/`
  3. Publish "landed" event to Pub/Sub with metadata
- **Output**: Raw JSON files in GCS, Pub/Sub message

### 2. **Orchestration** (Cloud Composer/Airflow)
- **Trigger**: Hourly schedule (`0 * * * *` in Asia/Bangkok timezone)
- **DAG Steps**:
  1. Trigger ingestor (HTTP call)
  2. Sensor: Wait for data in GCS partition (timeout: 10 min)
  3. Data quality gate: Validate file count & sizes
  4. Submit Spark cleanse job to Dataproc Serverless
  5. Run dbt models (staging → marts)
  6. Notify on success/failure (Slack)

### 3. **Cleansing** (Dataproc Serverless + Spark)
- **Trigger**: Airflow DAG
- **Process**:
  1. Read raw JSON from GCS partition
  2. Normalize into `weather_hourly` and `aqi_hourly` DataFrames
  3. Validate schema and data quality
  4. Quarantine bad records to `gs://bangkok-aqi-quarantine/`
  5. Write to BigQuery staging tables with MERGE (upsert by hour)
- **Output**: `staging_aqi.weather_hourly`, `staging_aqi.aqi_hourly`

### 4. **Transformation** (dbt + BigQuery)
- **Trigger**: Airflow DAG (after Spark)
- **Models**:
  1. **Staging**: `stg_weather`, `stg_aqi` (light transforms, views)
  2. **Dimension**: `dim_datetime` (hourly grain, table)
  3. **Fact**: `fact_aqi_hourly` (combined weather + AQI, incremental)
  4. **Mart**: `mart_daily_aqi_weather` (daily aggregates, table)
- **Output**: Analytics-ready tables in `marts_aqi`

### 5. **Serving** (Cloud Run + Streamlit)
- **Trigger**: User access via HTTPS
- **Process**:
  1. Query `marts_aqi.mart_daily_aqi_weather` via pandas-gbq
  2. Generate KPI cards, trend charts, data tables
  3. Refresh cache every 5 minutes
- **Output**: Interactive web dashboard

## Partitioning Strategy

### GCS (Raw Data)
- **Structure**: `gs://bucket/date=YYYY-MM-DD/hour=HH/*.json`
- **Retention**: 90 days (lifecycle policy)
- **Storage Class**: Standard → Nearline (30 days) → Delete (90 days)

### BigQuery (Staging Tables)
- **Partition**: Hourly on `event_hour` (TIMESTAMP)
- **Cluster**: By `source`
- **Expiration**: 90 days (automatic)
- **Use Case**: Temporary storage for cleansed data before dbt transforms

### BigQuery (Marts Tables)
- **fact_aqi_hourly**:
  - Partition: Hourly on `event_hour`
  - Cluster: By `date_local`
  - Materialization: Incremental (only new hours)
- **mart_daily_aqi_weather**:
  - Partition: Daily on `date`
  - Cluster: By `year`, `month`
  - Materialization: Full table refresh

## IAM Permissions Matrix

| Service Account | Role/Permission | Resource | Purpose |
|-----------------|----------------|----------|---------|
| `aqi-ingestor-sa` | `storage.objectCreator` | `bangkok-aqi-raw` | Write raw JSON |
| `aqi-ingestor-sa` | `pubsub.publisher` | `aqi-raw-landed` | Publish events |
| `aqi-ingestor-sa` | `secretmanager.secretAccessor` | Secrets | Access API keys |
| `aqi-dataproc-sa` | `storage.objectViewer` | `bangkok-aqi-raw` | Read raw data |
| `aqi-dataproc-sa` | `storage.objectCreator` | `bangkok-aqi-quarantine` | Write bad records |
| `aqi-dataproc-sa` | `bigquery.dataEditor` | `staging_aqi` | Write staging tables |
| `aqi-dataproc-sa` | `bigquery.jobUser` | Project | Run BQ jobs |
| `aqi-dataproc-sa` | `dataproc.worker` | Project | Execute Spark |
| `aqi-composer-sa` | `composer.worker` | Composer env | Run Airflow |
| `aqi-composer-sa` | `run.invoker` | Cloud Run services | Trigger ingestor |
| `aqi-composer-sa` | `dataproc.editor` | Project | Submit Spark jobs |
| `aqi-dbt-sa` | `bigquery.dataViewer` | `staging_aqi` | Read staging |
| `aqi-dbt-sa` | `bigquery.dataEditor` | `marts_aqi` | Write marts |
| `aqi-dbt-sa` | `bigquery.jobUser` | Project | Run dbt models |

## SLOs (Service Level Objectives)

### Data Freshness
- **Target**: Data for hour H available by H+02:00 (Bangkok time)
- **Measurement**: `MAX(ingested_at)` in `mart_daily_aqi_weather`
- **Alert**: If lag > 3 hours

### Data Completeness
- **Target**: ≥95% of hours per day have data
- **Measurement**: `hours_observed / 24` in `mart_daily_aqi_weather`
- **Alert**: If < 20 hours in any day

### Pipeline Success Rate
- **Target**: ≥98% of hourly DAG runs succeed
- **Measurement**: Airflow DAG success rate (last 7 days)
- **Alert**: If success rate < 95%

### Dashboard Availability
- **Target**: 99% uptime for Streamlit dashboard
- **Measurement**: Cloud Run uptime metrics
- **Alert**: If 5xx errors > 1% of requests

## Runbook

### Backfill Historical Data

```bash
# 1. Trigger ingestor for past hours
for hour in {0..23}; do
  curl -X POST "https://aqi-ingestor-xxx.run.app/ingest/hourly?hour_offset=-$hour"
  sleep 5
done

# 2. Submit Spark job for each hour
for hour in {0..23}; do
  gcloud dataproc batches submit pyspark \
    gs://bangkok-aqi-raw/spark/cleanse.py \
    --project=your-project-id \
    --region=asia-southeast1 \
    --service-account=aqi-dataproc-sa@your-project-id.iam.gserviceaccount.com \
    --version=2.1 \
    -- \
    --project_id your-project-id \
    --raw_bucket bangkok-aqi-raw \
    --quar_bucket bangkok-aqi-quarantine \
    --partition_date 2025-10-05 \
    --partition_hour $(printf "%02d" $hour)
done

# 3. Run dbt with full refresh
cd dbt
dbt run --full-refresh
dbt test
```

### Schema Change Policy

**Adding a column**:
1. Update Spark script to include new field
2. Deploy Spark job
3. Update dbt staging model
4. Update dbt downstream models
5. Deploy dbt models

**Removing a column**:
1. Update dbt models (remove references)
2. Deploy dbt
3. Update Spark script
4. Deploy Spark job

**Renaming a column**:
1. Add new column (follow "adding" process)
2. Backfill data
3. Remove old column (follow "removing" process)

### Incident Response

**No data for current hour**:
1. Check Cloud Run ingestor logs
2. Check Open-Meteo API status
3. Manually trigger ingestion
4. Check GCS for files
5. If files exist, re-run Spark job

**Airflow DAG failure**:
1. Check Airflow task logs
2. Identify failing task
3. Fix root cause
4. Clear failed task and retry

**BigQuery query timeout**:
1. Check query plan (explain)
2. Verify partition pruning is working
3. Check for missing cluster keys
4. Optimize dbt model if needed

## Cost Breakdown (Monthly Estimates)

| Service | Usage | Estimated Cost (USD) |
|---------|-------|---------------------|
| **Cloud Run (Ingestor)** | 720 requests/month, 5s avg | $0.10 |
| **Cloud Run (Dashboard)** | 1000 views/month, 10s avg | $0.50 |
| **GCS (Raw)** | 50 GB standard, 100 GB nearline | $2.50 |
| **GCS (Quarantine)** | 5 GB standard | $0.15 |
| **Pub/Sub** | 720 messages/month | $0.01 |
| **BigQuery (Storage)** | 100 GB active, 500 GB long-term | $5.00 |
| **BigQuery (Query)** | 1 TB/month scanned | $5.00 |
| **Dataproc Serverless** | 720 jobs × 2 min × 2 executors | $15.00 |
| **Cloud Composer** | Small environment (0.5 vCPU) | $75.00 |
| **Secret Manager** | 2 secrets, 720 access/month | $0.50 |
| **Cloud Logging** | 10 GB/month | $0.50 |
| **Egress** | 5 GB/month | $0.60 |
| **Total** | | **~$105/month** |

### Cost Optimization Tips

1. **Reduce Composer costs**:
   - Use SMALL environment (already configured)
   - Minimize worker count (1-3)
   - Delete old log files

2. **Reduce BigQuery costs**:
   - Use partitioning and clustering (already configured)
   - Set partition expiration (90 days)
   - Use materialized views for heavy queries

3. **Reduce Dataproc costs**:
   - Use Serverless (pay-per-job, not per-cluster)
   - Enable dynamic allocation
   - Optimize Spark jobs (fewer shuffles)

4. **Reduce GCS costs**:
   - Use lifecycle policies (already configured)
   - Move old data to Archive class
   - Delete unnecessary quarantine files

5. **Reduce Cloud Run costs**:
   - Set min instances = 0 (already configured)
   - Optimize container image size
   - Use cached queries in dashboard

## Security Best Practices

1. **No plaintext secrets**: All secrets in Secret Manager
2. **Least-privilege IAM**: Each SA has minimal permissions
3. **Private networking**: Use VPC-SC for sensitive workloads
4. **Audit logging**: Enable Cloud Audit Logs
5. **Data encryption**: At rest (default) and in transit (TLS)
6. **Access controls**: Restrict who can deploy and modify resources

## Monitoring & Alerting

### Key Metrics
- Cloud Run latency (p50, p95, p99)
- Airflow DAG success rate
- BigQuery query costs
- Data freshness lag
- Pipeline end-to-end latency

### Alerts (via Cloud Monitoring)
- Ingestor 5xx errors > 1%
- Airflow DAG failures
- Data lag > 3 hours
- BigQuery costs > $10/day
- GCS bucket > 200 GB

### Dashboards
- Cloud Monitoring: Infrastructure metrics
- Airflow UI: DAG runs and task logs
- Looker Studio: Business metrics (optional)

## Disaster Recovery

### Backup Strategy
- **GCS**: Versioning enabled (30-day retention)
- **BigQuery**: Automatic 7-day backup (time travel)
- **Terraform state**: Remote backend with locking

### Recovery Procedures

**Accidental data deletion**:
```sql
-- BigQuery time travel (up to 7 days)
SELECT * FROM `project.dataset.table`
FOR SYSTEM_TIME AS OF TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 1 DAY);
```

**Infrastructure corruption**:
```bash
# Restore from Terraform
cd infra/terraform
terraform plan
terraform apply
```

**Complete pipeline failure**:
1. Restore infrastructure (Terraform)
2. Backfill missing data (see Runbook)
3. Verify data quality (dbt test)
4. Resume normal operations

## References

- [Open-Meteo API Docs](https://open-meteo.com/en/docs)
- [BigQuery Partitioning Best Practices](https://cloud.google.com/bigquery/docs/partitioned-tables)
- [Dataproc Serverless Guide](https://cloud.google.com/dataproc-serverless/docs)
- [dbt Best Practices](https://docs.getdbt.com/best-practices)
- [Cloud Composer Optimization](https://cloud.google.com/composer/docs/composer-2/optimize-environments)
