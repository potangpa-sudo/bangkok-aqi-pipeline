output "dataset_staging_id" {
  description = "Staging dataset ID"
  value       = google_bigquery_dataset.staging.dataset_id
}

output "dataset_marts_id" {
  description = "Marts dataset ID"
  value       = google_bigquery_dataset.marts.dataset_id
}

output "table_weather_hourly_id" {
  description = "Weather hourly table ID"
  value       = google_bigquery_table.weather_hourly.table_id
}

output "table_aqi_hourly_id" {
  description = "AQI hourly table ID"
  value       = google_bigquery_table.aqi_hourly.table_id
}
