# Main topic for raw data landed events
resource "google_pubsub_topic" "main" {
  name    = var.topic_name
  project = var.project_id

  labels = merge(var.labels, {
    purpose = "raw-data-events"
  })

  message_retention_duration = "86400s" # 24 hours
}

# Dead letter queue topic
resource "google_pubsub_topic" "dlq" {
  name    = var.dlq_topic_name
  project = var.project_id

  labels = merge(var.labels, {
    purpose = "dead-letter-queue"
  })

  message_retention_duration = "604800s" # 7 days
}

# Subscription with DLQ
resource "google_pubsub_subscription" "main_sub" {
  name    = "${var.topic_name}-sub"
  project = var.project_id
  topic   = google_pubsub_topic.main.name

  ack_deadline_seconds = 20

  dead_letter_policy {
    dead_letter_topic     = google_pubsub_topic.dlq.id
    max_delivery_attempts = 5
  }

  retry_policy {
    minimum_backoff = "10s"
    maximum_backoff = "600s"
  }

  expiration_policy {
    ttl = "" # Never expire
  }

  labels = var.labels
}

# DLQ subscription for monitoring
resource "google_pubsub_subscription" "dlq_sub" {
  name    = "${var.dlq_topic_name}-sub"
  project = var.project_id
  topic   = google_pubsub_topic.dlq.name

  ack_deadline_seconds = 20

  expiration_policy {
    ttl = "" # Never expire
  }

  labels = var.labels
}
