output "topic_id" {
  description = "Main Pub/Sub topic ID"
  value       = google_pubsub_topic.main.id
}

output "topic_name" {
  description = "Main Pub/Sub topic name"
  value       = google_pubsub_topic.main.name
}

output "dlq_topic_id" {
  description = "DLQ topic ID"
  value       = google_pubsub_topic.dlq.id
}

output "dlq_topic_name" {
  description = "DLQ topic name"
  value       = google_pubsub_topic.dlq.name
}

output "subscription_id" {
  description = "Main subscription ID"
  value       = google_pubsub_subscription.main_sub.id
}
