# Placeholder secrets for external API keys and credentials
# Users should populate these via `gcloud secrets versions add`

resource "google_secret_manager_secret" "api_keys" {
  secret_id = "aqi-api-keys"
  project   = var.project_id

  labels = merge(var.labels, {
    purpose = "api-credentials"
  })

  replication {
    auto {}
  }
}

resource "google_secret_manager_secret" "slack_webhook" {
  secret_id = "aqi-slack-webhook"
  project   = var.project_id

  labels = merge(var.labels, {
    purpose = "alerting"
  })

  replication {
    auto {}
  }
}

# Note: Secret values must be added manually via:
# gcloud secrets versions add aqi-api-keys --data-file=- <<< "your-api-key"
# gcloud secrets versions add aqi-slack-webhook --data-file=- <<< "https://hooks.slack.com/..."
