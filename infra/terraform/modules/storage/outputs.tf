output "bucket_raw_name" {
  description = "Raw data bucket name"
  value       = google_storage_bucket.raw.name
}

output "bucket_raw_url" {
  description = "Raw data bucket URL"
  value       = google_storage_bucket.raw.url
}

output "bucket_quarantine_name" {
  description = "Quarantine bucket name"
  value       = google_storage_bucket.quarantine.name
}

output "bucket_quarantine_url" {
  description = "Quarantine bucket URL"
  value       = google_storage_bucket.quarantine.url
}
