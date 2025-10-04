output "api_keys_secret_id" {
  description = "API keys secret ID"
  value       = google_secret_manager_secret.api_keys.secret_id
}

output "slack_webhook_secret_id" {
  description = "Slack webhook secret ID"
  value       = google_secret_manager_secret.slack_webhook.secret_id
}
