variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "region" {
  description = "GCP region for Cloud Composer"
  type        = string
}

variable "environment_name" {
  description = "Cloud Composer environment name"
  type        = string
}

variable "service_account_email" {
  description = "Service account for Composer"
  type        = string
}

variable "labels" {
  description = "Common labels"
  type        = map(string)
  default     = {}
}

variable "node_count" {
  description = "Number of nodes in the environment"
  type        = number
  default     = 3
}

variable "machine_type" {
  description = "Machine type for Composer nodes"
  type        = string
  default     = "n1-standard-1"
}

variable "disk_size_gb" {
  description = "Disk size for Composer nodes in GB"
  type        = number
  default     = 30
}

variable "python_version" {
  description = "Python version for Airflow"
  type        = string
  default     = "3"
}

variable "airflow_config_overrides" {
  description = "Airflow configuration overrides"
  type        = map(string)
  default = {
    "core-dags_are_paused_at_creation" = "True"
    "core-default_timezone"            = "Asia/Bangkok"
  }
}

variable "env_variables" {
  description = "Environment variables for Airflow"
  type        = map(string)
  default     = {}
}
