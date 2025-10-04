output "project_id" {
  description = "GCP Project ID"
  value       = var.project_id
}

output "region" {
  description = "GCP Region"
  value       = var.region
}

# Storage Outputs
output "gcs_bucket_raw_name" {
  description = "Raw data GCS bucket name"
  value       = module.storage.bucket_raw_name
}

output "gcs_bucket_raw_url" {
  description = "Raw data GCS bucket URL"
  value       = module.storage.bucket_raw_url
}

output "gcs_bucket_quarantine_name" {
  description = "Quarantine GCS bucket name"
  value       = module.storage.bucket_quarantine_name
}

output "gcs_bucket_quarantine_url" {
  description = "Quarantine GCS bucket URL"
  value       = module.storage.bucket_quarantine_url
}

# Pub/Sub Outputs
output "pubsub_topic_id" {
  description = "Pub/Sub topic ID for raw data events"
  value       = module.pubsub.topic_id
}

output "pubsub_dlq_topic_id" {
  description = "Pub/Sub DLQ topic ID"
  value       = module.pubsub.dlq_topic_id
}

# BigQuery Outputs
output "bq_dataset_staging_id" {
  description = "BigQuery staging dataset ID"
  value       = module.bigquery.dataset_staging_id
}

output "bq_dataset_marts_id" {
  description = "BigQuery marts dataset ID"
  value       = module.bigquery.dataset_marts_id
}

# Cloud Run Outputs
output "ingestor_service_url" {
  description = "Cloud Run ingestor service URL"
  value       = module.cloud_run_ingestor.service_url
}

output "dashboard_service_url" {
  description = "Cloud Run dashboard service URL"
  value       = module.cloud_run_dashboard.service_url
}

# IAM Outputs
output "ingestor_sa_email" {
  description = "Ingestor service account email"
  value       = module.iam.ingestor_sa_email
}

output "dataproc_sa_email" {
  description = "Dataproc service account email"
  value       = module.iam.dataproc_sa_email
}

output "composer_sa_email" {
  description = "Composer service account email"
  value       = module.iam.composer_sa_email
}

output "dbt_sa_email" {
  description = "dbt service account email"
  value       = module.iam.dbt_sa_email
}

# Composer Outputs
output "composer_environment_name" {
  description = "Cloud Composer environment name"
  value       = module.composer.environment_name
}

output "composer_airflow_uri" {
  description = "Cloud Composer Airflow web UI URL"
  value       = module.composer.airflow_uri
}

output "composer_gcs_bucket" {
  description = "Cloud Composer GCS bucket for DAGs"
  value       = module.composer.gcs_bucket
}

# Summary Output
output "deployment_summary" {
  description = "Deployment summary with key endpoints"
  value = {
    ingestor_url         = module.cloud_run_ingestor.service_url
    dashboard_url        = module.cloud_run_dashboard.service_url
    composer_env         = module.composer.environment_name
    composer_airflow_uri = module.composer.airflow_uri
    raw_bucket           = "gs://${module.storage.bucket_raw_name}"
    quarantine_bucket    = "gs://${module.storage.bucket_quarantine_name}"
    staging_dataset      = "${var.project_id}.${module.bigquery.dataset_staging_id}"
    marts_dataset        = "${var.project_id}.${module.bigquery.dataset_marts_id}"
  }
}
