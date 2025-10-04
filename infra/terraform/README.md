# Bangkok AQI Pipeline - Terraform

This directory contains Terraform infrastructure-as-code for deploying the Bangkok AQI pipeline to Google Cloud Platform.

## Prerequisites

- Terraform >= 1.5.0
- GCP Project with billing enabled
- `gcloud` CLI authenticated
- Required GCP APIs enabled (automatically enabled by Terraform)

## Quick Start

1. **Initialize Terraform**
   ```bash
   cd infra/terraform
   terraform init
   ```

2. **Configure Variables**
   ```bash
   cp terraform.tfvars.example terraform.tfvars
   # Edit terraform.tfvars with your project details
   ```

3. **Plan Infrastructure**
   ```bash
   terraform plan
   ```

4. **Deploy Infrastructure**
   ```bash
   terraform apply
   ```

5. **View Outputs**
   ```bash
   terraform output
   terraform output -json deployment_summary
   ```

## Module Structure

```
modules/
├── iam/                  # Service accounts and permissions
├── storage/              # GCS buckets with lifecycle policies
├── pubsub/               # Pub/Sub topics and subscriptions
├── bq/                   # BigQuery datasets and tables
├── run/                  # Cloud Run services
├── composer/             # Cloud Composer (Airflow) environment
├── dataproc_serverless/  # Dataproc Serverless configuration
└── secrets/              # Secret Manager placeholders
```

## Required Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `project_id` | GCP Project ID | - (required) |
| `region` | Primary GCP region | `asia-southeast1` |
| `gcs_bucket_raw` | Raw data bucket name | - (required) |
| `gcs_bucket_quarantine` | Quarantine bucket name | - (required) |

See `variables.tf` for all available variables.

## Key Outputs

- `ingestor_service_url` - Cloud Run ingestor endpoint
- `dashboard_service_url` - Cloud Run dashboard endpoint
- `composer_airflow_uri` - Airflow web UI
- `bq_dataset_staging_id` - Staging dataset
- `bq_dataset_marts_id` - Marts dataset

## Cost Optimization

- Cloud Composer uses SMALL environment (lowest cost)
- Cloud Run scales to zero when idle
- GCS has lifecycle policies (90-day deletion, 30-day Nearline)
- BigQuery staging tables expire after 90 days
- Dataproc Serverless is pay-per-job

## Cleanup

To destroy all resources:
```bash
terraform destroy
```

⚠️ **Warning**: This will delete all data and infrastructure!

## Next Steps

After deploying infrastructure:
1. Build and deploy Cloud Run services (see `/src/ingestor/README.md`)
2. Upload Airflow DAGs to Composer (see `/airflow/README.md`)
3. Deploy Spark job (see `/spark/README.md`)
4. Run dbt models (see `/dbt/README.md`)
