data "aws_region" "current" {}

output "pool_id" {
  description = "The ID of the Cognito User Pool"
  value       = aws_cognito_user_pool.pool.id
}

output "pool_arn" {
  description = "The ARN of the Cognito User Pool"
  value       = aws_cognito_user_pool.pool.arn

}

output "client_id" {
  description = "The ID of the Cognito User Pool Client"
  value       = aws_cognito_user_pool_client.client.id
}

output "cognito_authorizer_id" {
  description = "The ID of the API Gateway Cognito Authorizer"
  value       = aws_api_gateway_authorizer.cognito_authorizer.id
}

output "domain" {
  description = "The domain of the Cognito User Pool"
  value       = "${aws_cognito_user_pool_domain.domain.domain}.auth.${data.aws_region.current.id}.amazoncognito.com"
}