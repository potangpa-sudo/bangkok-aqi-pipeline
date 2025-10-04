output "environment_name" {
  description = "Composer environment name"
  value       = google_composer_environment.composer_env.name
}

output "environment_id" {
  description = "Composer environment ID"
  value       = google_composer_environment.composer_env.id
}

output "gcs_bucket" {
  description = "GCS bucket for DAGs"
  value       = google_composer_environment.composer_env.config[0].dag_gcs_prefix
}

output "airflow_uri" {
  description = "Airflow web UI URL"
  value       = google_composer_environment.composer_env.config[0].airflow_uri
}
