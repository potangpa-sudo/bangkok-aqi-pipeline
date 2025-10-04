# Service Account for Cloud Run Ingestor
resource "google_service_account" "ingestor" {
  account_id   = "aqi-ingestor-sa"
  display_name = "AQI Ingestor Service Account"
  description  = "Service account for Cloud Run ingestor service"
  project      = var.project_id
}

# Service Account for Dataproc Serverless
resource "google_service_account" "dataproc" {
  account_id   = "aqi-dataproc-sa"
  display_name = "AQI Dataproc Service Account"
  description  = "Service account for Dataproc Serverless batch jobs"
  project      = var.project_id
}

# Service Account for Cloud Composer
resource "google_service_account" "composer" {
  account_id   = "aqi-composer-sa"
  display_name = "AQI Composer Service Account"
  description  = "Service account for Cloud Composer environment"
  project      = var.project_id
}

# Service Account for dbt
resource "google_service_account" "dbt" {
  account_id   = "aqi-dbt-sa"
  display_name = "AQI dbt Service Account"
  description  = "Service account for dbt transformations"
  project      = var.project_id
}

# ===========================
# Ingestor Service Account Permissions
# ===========================

# GCS - Write to raw bucket
resource "google_storage_bucket_iam_member" "ingestor_raw_writer" {
  bucket = var.gcs_bucket_raw
  role   = "roles/storage.objectCreator"
  member = "serviceAccount:${google_service_account.ingestor.email}"
}

# Pub/Sub - Publish to topic
resource "google_pubsub_topic_iam_member" "ingestor_publisher" {
  project = var.project_id
  topic   = var.pubsub_topic
  role    = "roles/pubsub.publisher"
  member  = "serviceAccount:${google_service_account.ingestor.email}"
}

# Secret Manager - Access secrets
resource "google_project_iam_member" "ingestor_secret_accessor" {
  project = var.project_id
  role    = "roles/secretmanager.secretAccessor"
  member  = "serviceAccount:${google_service_account.ingestor.email}"
}

# ===========================
# Dataproc Service Account Permissions
# ===========================

# GCS - Read from raw, write to staging and quarantine
resource "google_storage_bucket_iam_member" "dataproc_raw_reader" {
  bucket = var.gcs_bucket_raw
  role   = "roles/storage.objectViewer"
  member = "serviceAccount:${google_service_account.dataproc.email}"
}

resource "google_storage_bucket_iam_member" "dataproc_quar_writer" {
  bucket = var.gcs_bucket_quarantine
  role   = "roles/storage.objectCreator"
  member = "serviceAccount:${google_service_account.dataproc.email}"
}

# BigQuery - Write to staging dataset
resource "google_bigquery_dataset_iam_member" "dataproc_staging_editor" {
  project    = var.project_id
  dataset_id = var.bq_dataset_staging
  role       = "roles/bigquery.dataEditor"
  member     = "serviceAccount:${google_service_account.dataproc.email}"
}

# BigQuery - Job user for running queries
resource "google_project_iam_member" "dataproc_bq_job_user" {
  project = var.project_id
  role    = "roles/bigquery.jobUser"
  member  = "serviceAccount:${google_service_account.dataproc.email}"
}

# Dataproc - Worker role
resource "google_project_iam_member" "dataproc_worker" {
  project = var.project_id
  role    = "roles/dataproc.worker"
  member  = "serviceAccount:${google_service_account.dataproc.email}"
}

# ===========================
# Composer Service Account Permissions
# ===========================

# Composer - Worker role
resource "google_project_iam_member" "composer_worker" {
  project = var.project_id
  role    = "roles/composer.worker"
  member  = "serviceAccount:${google_service_account.composer.email}"
}

# Cloud Run - Invoker for triggering services
resource "google_project_iam_member" "composer_run_invoker" {
  project = var.project_id
  role    = "roles/run.invoker"
  member  = "serviceAccount:${google_service_account.composer.email}"
}

# Dataproc - Editor for submitting batch jobs
resource "google_project_iam_member" "composer_dataproc_editor" {
  project = var.project_id
  role    = "roles/dataproc.editor"
  member  = "serviceAccount:${google_service_account.composer.email}"
}

# GCS - Read/write for DAGs and data
resource "google_storage_bucket_iam_member" "composer_raw_reader" {
  bucket = var.gcs_bucket_raw
  role   = "roles/storage.objectViewer"
  member = "serviceAccount:${google_service_account.composer.email}"
}

# BigQuery - Data viewer for checking pipeline status
resource "google_bigquery_dataset_iam_member" "composer_staging_viewer" {
  project    = var.project_id
  dataset_id = var.bq_dataset_staging
  role       = "roles/bigquery.dataViewer"
  member     = "serviceAccount:${google_service_account.composer.email}"
}

resource "google_bigquery_dataset_iam_member" "composer_marts_viewer" {
  project    = var.project_id
  dataset_id = var.bq_dataset_marts
  role       = "roles/bigquery.dataViewer"
  member     = "serviceAccount:${google_service_account.composer.email}"
}

# ===========================
# dbt Service Account Permissions
# ===========================

# BigQuery - Read from staging, write to marts
resource "google_bigquery_dataset_iam_member" "dbt_staging_viewer" {
  project    = var.project_id
  dataset_id = var.bq_dataset_staging
  role       = "roles/bigquery.dataViewer"
  member     = "serviceAccount:${google_service_account.dbt.email}"
}

resource "google_bigquery_dataset_iam_member" "dbt_marts_editor" {
  project    = var.project_id
  dataset_id = var.bq_dataset_marts
  role       = "roles/bigquery.dataEditor"
  member     = "serviceAccount:${google_service_account.dbt.email}"
}

# BigQuery - Job user
resource "google_project_iam_member" "dbt_bq_job_user" {
  project = var.project_id
  role    = "roles/bigquery.jobUser"
  member  = "serviceAccount:${google_service_account.dbt.email}"
}
