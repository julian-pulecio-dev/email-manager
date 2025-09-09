variable "api_id" {
  description = "The API Gateway REST API"
  type        = string

}

variable "name" {
  description = "The name of the Cognito User Pool"
  type        = string
  default     = "email_manager_user_pool"
}

variable "google_client_id" {
  description = "Google OAuth Client ID"
  type        = string
  sensitive   = true
}

variable "google_client_secret" {
  description = "Google OAuth Client Secret"
  type        = string
  sensitive   = true
}

variable "domain_name" {
  description = "value"
  type        = string
}