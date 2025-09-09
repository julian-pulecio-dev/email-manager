resource "google_pubsub_topic" "my_topic" {
  name = var.topic_name
}

# Crear una suscripción tipo PUSH hacia API Gateway
resource "google_pubsub_subscription" "my_subscription" {
  name  = var.subscription_name
  topic = google_pubsub_topic.my_topic.id

  ack_deadline_seconds       = 20
  message_retention_duration = "86400s" # 1 día

  push_config {
    # API Gateway endpoint en AWS que recibirá los mensajes de Pub/Sub
    push_endpoint = var.api_gateway_endpoint

    # OIDC token firmado por una Service Account de GCP
    oidc_token {
      service_account_email = var.push_service_account
    }
  }
}