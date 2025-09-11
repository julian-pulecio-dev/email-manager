output "arn" {
  value       = aws_iam_policy.cognito_policy.arn
  description = "The ARN of the Cognito policy"
}