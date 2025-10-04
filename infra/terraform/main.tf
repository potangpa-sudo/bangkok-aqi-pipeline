# Enable required GCP APIs
resource "google_project_service" "required_apis" {
  for_each = toset([
    "storage.googleapis.com",
    "bigquery.googleapis.com",
    "pubsub.googleapis.com",
    "run.googleapis.com",
    "composer.googleapis.com",
    "dataproc.googleapis.com",
    "secretmanager.googleapis.com",
    "iam.googleapis.com",
    "cloudresourcemanager.googleapis.com",
    "compute.googleapis.com",
    "servicenetworking.googleapis.com",
  ])

  service            = each.value
  disable_on_destroy = false
}

# IAM Module - Service Accounts and Permissions
module "iam" {
  source = "./modules/iam"

  project_id              = var.project_id
  region                  = var.region
  gcs_bucket_raw          = var.gcs_bucket_raw
  gcs_bucket_quarantine   = var.gcs_bucket_quarantine
  bq_dataset_staging      = var.bq_dataset_staging
  bq_dataset_marts        = var.bq_dataset_marts
  pubsub_topic            = var.pubsub_topic
  labels                  = var.labels

  depends_on = [google_project_service.required_apis]
}

# Storage Module - GCS Buckets
module "storage" {
  source = "./modules/storage"

  project_id            = var.project_id
  region                = var.region
  gcs_bucket_raw        = var.gcs_bucket_raw
  gcs_bucket_quarantine = var.gcs_bucket_quarantine
  labels                = var.labels

  depends_on = [google_project_service.required_apis]
}

# Pub/Sub Module
module "pubsub" {
  source = "./modules/pubsub"

  project_id      = var.project_id
  topic_name      = var.pubsub_topic
  dlq_topic_name  = var.pubsub_dlq_topic
  labels          = var.labels

  depends_on = [google_project_service.required_apis]
}

# BigQuery Module
module "bigquery" {
  source = "./modules/bq"

  project_id      = var.project_id
  location        = var.bq_location
  dataset_staging = var.bq_dataset_staging
  dataset_marts   = var.bq_dataset_marts
  labels          = var.labels

  depends_on = [google_project_service.required_apis]
}

# Secret Manager Module
module "secrets" {
  source = "./modules/secrets"

  project_id = var.project_id
  region     = var.region
  labels     = var.labels

  depends_on = [google_project_service.required_apis]
}

# Cloud Run Module - Ingestor Service
module "cloud_run_ingestor" {
  source = "./modules/run"

  project_id            = var.project_id
  region                = var.region
  service_name          = var.ingestor_service_name
  service_account_email = module.iam.ingestor_sa_email
  image                 = "gcr.io/${var.project_id}/${var.ingestor_service_name}:latest"
  
  env_vars = {
    GCP_PROJECT_ID        = var.project_id
    GCP_REGION            = var.region
    GCS_BUCKET_RAW        = var.gcs_bucket_raw
    GCS_BUCKET_QUAR       = var.gcs_bucket_quarantine
    PUBSUB_TOPIC          = var.pubsub_topic
    OPEN_METEO_BASE       = "https://api.open-meteo.com/v1"
    TIMEZONE              = "Asia/Bangkok"
  }

  labels = var.labels

  depends_on = [
    module.iam,
    google_project_service.required_apis
  ]
}

# Cloud Run Module - Dashboard Service
module "cloud_run_dashboard" {
  source = "./modules/run"

  project_id            = var.project_id
  region                = var.region
  service_name          = var.dashboard_service_name
  service_account_email = module.iam.ingestor_sa_email  # Reuse for now, can separate later
  image                 = "gcr.io/${var.project_id}/${var.dashboard_service_name}:latest"
  
  env_vars = {
    GCP_PROJECT_ID       = var.project_id
    BQ_DATASET_MARTS     = var.bq_dataset_marts
    MODE                 = "bigquery"
  }

  labels = var.labels

  depends_on = [
    module.iam,
    google_project_service.required_apis
  ]
}

# Dataproc Serverless Module
module "dataproc_serverless" {
  source = "./modules/dataproc_serverless"

  project_id            = var.project_id
  region                = var.region
  service_account_email = module.iam.dataproc_sa_email
  labels                = var.labels

  depends_on = [
    module.iam,
    google_project_service.required_apis
  ]
}

# Cloud Composer Module
module "composer" {
  source = "./modules/composer"

  project_id            = var.project_id
  region                = var.composer_location
  environment_name      = var.composer_env_name
  service_account_email = module.iam.composer_sa_email
  labels                = var.labels

  depends_on = [
    module.iam,
    google_project_service.required_apis
  ]
}
