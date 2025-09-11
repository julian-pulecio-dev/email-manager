output "arn" {
    value       = aws_sqs_queue.terraform_queue.arn
    description = "The ARN of the SQS queue"
}

output "url" {
    value       = aws_sqs_queue.terraform_queue.url
    description = "The URL of the SQS queue"
}