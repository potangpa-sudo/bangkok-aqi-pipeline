variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "region" {
  description = "GCP region for resources"
  type        = string
  default     = "asia-southeast1"
}

variable "zone" {
  description = "GCP zone for zonal resources"
  type        = string
  default     = "asia-southeast1-a"
}

variable "bq_location" {
  description = "BigQuery dataset location"
  type        = string
  default     = "asia-southeast1"
}

variable "bq_dataset_staging" {
  description = "BigQuery staging dataset name"
  type        = string
  default     = "staging_aqi"
}

variable "bq_dataset_marts" {
  description = "BigQuery marts dataset name"
  type        = string
  default     = "marts_aqi"
}

variable "gcs_bucket_raw" {
  description = "GCS bucket for raw data"
  type        = string
}

variable "gcs_bucket_quarantine" {
  description = "GCS bucket for quarantined/bad records"
  type        = string
}

variable "pubsub_topic" {
  description = "Pub/Sub topic name for raw data landed events"
  type        = string
  default     = "aqi-raw-landed"
}

variable "pubsub_dlq_topic" {
  description = "Pub/Sub dead letter queue topic"
  type        = string
  default     = "aqi-raw-dlq"
}

variable "ingestor_service_name" {
  description = "Cloud Run service name for ingestor"
  type        = string
  default     = "aqi-ingestor"
}

variable "dashboard_service_name" {
  description = "Cloud Run service name for dashboard"
  type        = string
  default     = "aqi-dashboard"
}

variable "composer_env_name" {
  description = "Cloud Composer environment name"
  type        = string
  default     = "bangkok-aqi-composer"
}

variable "composer_location" {
  description = "Cloud Composer location"
  type        = string
  default     = "asia-southeast1"
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "labels" {
  description = "Common labels for all resources"
  type        = map(string)
  default = {
    project     = "bangkok-aqi"
    managed_by  = "terraform"
  }
}
