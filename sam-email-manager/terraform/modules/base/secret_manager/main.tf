data "aws_secretsmanager_secret" "credentials" {
  name = var.secret_name
}

data "aws_secretsmanager_secret_version" "credentials" {
  secret_id = data.aws_secretsmanager_secret.credentials.id
}