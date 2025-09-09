output "decoded_secret" {
  description = "The decoded secret from AWS Secrets Manager"
  value       = jsondecode(data.aws_secretsmanager_secret_version.credentials.secret_string)
  sensitive   = true
}