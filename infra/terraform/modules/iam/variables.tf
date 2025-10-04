variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "region" {
  description = "GCP region"
  type        = string
}

variable "gcs_bucket_raw" {
  description = "Raw data bucket name"
  type        = string
}

variable "gcs_bucket_quarantine" {
  description = "Quarantine bucket name"
  type        = string
}

variable "bq_dataset_staging" {
  description = "BigQuery staging dataset"
  type        = string
}

variable "bq_dataset_marts" {
  description = "BigQuery marts dataset"
  type        = string
}

variable "pubsub_topic" {
  description = "Pub/Sub topic name"
  type        = string
}

variable "labels" {
  description = "Common labels"
  type        = map(string)
  default     = {}
}
