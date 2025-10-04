# Bangkok AQI - dbt Project

dbt (data build tool) project for transforming Bangkok air quality and weather data in BigQuery.

## Overview

This dbt project:
- Sources data from BigQuery staging tables (populated by Spark)
- Creates staging views with light transformations
- Builds dimensional models (datetime dimension)
- Creates fact tables at hourly grain
- Aggregates to daily marts for analytics

## Project Structure

```
dbt/
├── dbt_project.yml          # Project configuration
├── profiles.yml             # BigQuery connection profiles
├── models/
│   ├── sources.yml          # Source table definitions
│   ├── schema.yml           # Model docs and tests
│   ├── staging/             # Staging views
│   │   ├── stg_weather.sql
│   │   └── stg_aqi.sql
│   └── marts/
│       ├── dimensions/
│       │   └── dim_datetime.sql
│       ├── facts/
│       │   └── fact_aqi_hourly.sql
│       └── aggregates/
│           └── mart_daily_aqi_weather.sql
├── tests/                   # Custom tests
├── macros/                  # Reusable SQL macros
└── docs/                    # Documentation
```

## Lineage

```
staging.weather_hourly  ─┐
                          ├─> stg_weather ─┐
                          │                 │
staging.aqi_hourly  ─────┼─> stg_aqi ──────┼─> fact_aqi_hourly ──> mart_daily_aqi_weather
                          │                 │
                          └─> dim_datetime ─┘
```

## Setup

### Prerequisites

- Python 3.11+
- GCP Project with BigQuery enabled
- Service account with BigQuery access
- BigQuery staging tables populated (via Spark cleanse job)

### Installation

```bash
cd dbt
pip install -r requirements.txt
```

### Configuration

1. **Set environment variables**:

```bash
export GCP_PROJECT_ID=your-project-id
export DBT_SERVICE_ACCOUNT_PATH=/path/to/service-account-key.json
```

2. **Update `profiles.yml`** with your project details

3. **Verify connection**:

```bash
dbt debug
```

## Usage

### Run All Models

```bash
dbt run
```

### Run Specific Models

```bash
# Run staging models only
dbt run --select staging

# Run marts only
dbt run --select marts

# Run specific model and downstream
dbt run --select stg_weather+

# Run specific model only
dbt run --select fact_aqi_hourly
```

### Incremental Runs

The `fact_aqi_hourly` model is incremental. To process new data only:

```bash
dbt run --select fact_aqi_hourly
```

### Run Tests

```bash
# Run all tests
dbt test

# Test specific model
dbt test --select stg_aqi

# Test with increased severity
dbt test --select stg_aqi --fail-fast
```

### Generate Documentation

```bash
# Generate docs
dbt docs generate

# Serve docs locally
dbt docs serve
```

### Full Refresh

To rebuild incremental models from scratch:

```bash
dbt run --full-refresh --select fact_aqi_hourly
```

## Model Details

### Staging Layer

**stg_weather**: Light transformations on weather data
- Temperature unit conversions (C to F)
- Rounding and formatting
- Anomaly detection flags
- Derived date/hour fields

**stg_aqi**: Light transformations on air quality data
- Pollutant rounding
- US AQI category mapping
- PM2.5 proxy AQI calculation
- Anomaly detection flags

### Marts Layer

**dim_datetime**: Datetime dimension
- Hourly grain
- Date/time components (year, month, day, hour)
- Named components (day name, month name)
- Boolean flags (is_weekend, is_daytime, is_rush_hour)

**fact_aqi_hourly**: Hourly fact table (incremental)
- Combines weather + air quality
- Enriched with datetime dimension
- Partition by hour, cluster by date
- Incremental updates (only new hours)

**mart_daily_aqi_weather**: Daily aggregate mart
- Daily averages, mins, maxs for all metrics
- P95 PM2.5
- Unhealthy hour counts
- Most common AQI category
- Data quality summaries

## Testing Strategy

### Built-in Tests
- `not_null`: Critical fields must exist
- `unique`: Primary keys must be unique
- `accepted_values`: Categorical fields have valid values
- `dbt_utils.accepted_range`: Numeric fields within expected ranges

### Custom Tests (TODO)
- Data freshness (last updated < 2 hours ago)
- Completeness (hours_observed = 24 for complete days)
- Cross-dataset consistency (staging vs marts counts)

## Deployment

### In Airflow (Recommended)

The Airflow DAG (`airflow/dags/aqi_hourly.py`) automatically runs dbt after Spark cleanse:

```python
dbt_run = BashOperator(
    task_id="dbt_run",
    bash_command="""
    cd /opt/airflow/dbt && \
    dbt run --select staging+ && \
    dbt test --select staging+
    """
)
```

### Standalone

```bash
# Set variables for specific execution
dbt run --vars '{"execution_date": "2025-10-05", "execution_hour": "14"}'
```

## CI/CD Integration

### Pre-commit Checks

```bash
# Lint SQL
dbt parse

# Compile without running
dbt compile

# Run on CI profile
dbt run --target ci
```

### GitHub Actions

See `.github/workflows/ci.yml` for full CI pipeline:
- SQL linting
- dbt compile
- dbt test (dry run)

## Cost Optimization

- **Partitioning**: Hourly partitions on fact tables, daily on marts
- **Clustering**: Cluster by date and common filter fields
- **Incremental models**: Only process new data
- **Partition pruning**: Filters on partition keys reduce scan costs
- **Table materialization**: Marts materialized for fast queries

## Monitoring

### Check Model Runs

```sql
SELECT *
FROM `your-project-id.marts_aqi.mart_daily_aqi_weather`
WHERE dbt_updated_at > TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 1 HOUR)
ORDER BY date DESC;
```

### Data Freshness

```sql
SELECT
    MAX(date) as latest_date,
    MAX(last_ingested_at) as latest_ingestion,
    TIMESTAMP_DIFF(CURRENT_TIMESTAMP(), MAX(last_ingested_at), HOUR) as hours_since_last_ingest
FROM `your-project-id.marts_aqi.mart_daily_aqi_weather`;
```

## Troubleshooting

### Connection Issues

```bash
# Verify service account
gcloud auth activate-service-account --key-file=$DBT_SERVICE_ACCOUNT_PATH

# Test connection
dbt debug
```

### Model Failures

```bash
# View logs
cat logs/dbt.log

# Run with verbose logging
dbt run --select failing_model --debug
```

### Incremental Issues

```bash
# Force full refresh
dbt run --select fact_aqi_hourly --full-refresh

# Check state
SELECT MAX(event_hour) FROM `your-project-id.marts_aqi.fact_aqi_hourly`;
```

## Next Steps

1. Add data freshness tests (dbt source freshness)
2. Implement custom generic tests
3. Add more business logic tests
4. Create dbt exposures for downstream dashboards
5. Implement dbt Cloud for scheduled runs
