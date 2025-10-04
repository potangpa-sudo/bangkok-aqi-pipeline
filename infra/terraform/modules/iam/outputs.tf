output "ingestor_sa_email" {
  description = "Ingestor service account email"
  value       = google_service_account.ingestor.email
}

output "dataproc_sa_email" {
  description = "Dataproc service account email"
  value       = google_service_account.dataproc.email
}

output "composer_sa_email" {
  description = "Composer service account email"
  value       = google_service_account.composer.email
}

output "dbt_sa_email" {
  description = "dbt service account email"
  value       = google_service_account.dbt.email
}
