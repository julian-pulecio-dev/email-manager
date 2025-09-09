output "arn" {
  value       = aws_iam_policy.dynamodb_policy.arn
  description = "The ARN of the DynamoDB policy"
}