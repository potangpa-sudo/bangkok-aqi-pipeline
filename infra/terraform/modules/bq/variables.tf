variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "location" {
  description = "BigQuery dataset location"
  type        = string
}

variable "dataset_staging" {
  description = "Staging dataset name"
  type        = string
}

variable "dataset_marts" {
  description = "Marts dataset name"
  type        = string
}

variable "labels" {
  description = "Common labels"
  type        = map(string)
  default     = {}
}
