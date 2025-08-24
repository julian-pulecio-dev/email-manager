variable "project_id" {
  description = "ID del proyecto de GCP"
  type        = string
}

variable "region" {
  description = "Región por defecto para el provider"
  type        = string
  default     = "us-central1"
}

variable "topic_name" {
  description = "Nombre del Pub/Sub topic"
  type        = string
  default     = "my-topic"
}

variable "subscription_name" {
  description = "Nombre de la suscripción"
  type        = string
  default     = "my-subscription"
}

# Endpoint de tu API Gateway en AWS (ejemplo: https://abc123.execute-api.us-east-1.amazonaws.com/prod/pubsub)
variable "api_gateway_endpoint" {
  description = "URL HTTPS de API Gateway en AWS que recibirá los mensajes de Pub/Sub"
  type        = string
}

# Cuenta de servicio en GCP que Pub/Sub usará para firmar las llamadas con OIDC
variable "push_service_account" {
  description = "Email de la service account de GCP usada para firmar el token OIDC"
  type        = string
}
