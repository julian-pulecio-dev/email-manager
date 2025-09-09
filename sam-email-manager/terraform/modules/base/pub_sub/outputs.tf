# ID completo del topic
output "topic_id" {
  description = "ID del topic Pub/Sub"
  value       = google_pubsub_topic.my_topic.id
}

# Nombre del topic
output "topic_name" {
  description = "Nombre del topic Pub/Sub"
  value       = google_pubsub_topic.my_topic.name
}

# ID completo de la suscripción
output "subscription_id" {
  description = "ID de la suscripción Pub/Sub"
  value       = google_pubsub_subscription.my_subscription.id
}

# Nombre de la suscripción
output "subscription_name" {
  description = "Nombre de la suscripción Pub/Sub"
  value       = google_pubsub_subscription.my_subscription.name
}

# Endpoint configurado para la suscripción push
output "subscription_push_endpoint" {
  description = "Endpoint HTTPS al que Pub/Sub enviará mensajes"
  value       = google_pubsub_subscription.my_subscription.push_config[0].push_endpoint
}

# Service Account usada para firmar el token OIDC
output "subscription_push_service_account" {
  description = "Cuenta de servicio usada para firmar requests push"
  value       = try(google_pubsub_subscription.my_subscription.push_config[0].oidc_token[0].service_account_email, null)
}