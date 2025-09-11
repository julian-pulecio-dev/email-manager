output "arn" {
  value       = aws_iam_policy.sqs_queue_policy.arn
  description = "The ARN of the SQS Queue policy"
}