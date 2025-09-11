resource "aws_iam_policy" "sqs_queue_policy" {
  name        = "lambda_sqs_queue_policy"
  description = "Allow Lambda to access SQS Queues"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "sqs:SendMessage",
          "sqs:ReceiveMessage",
          "sqs:DeleteMessage",
          "sqs:GetQueueAttributes"
        ]
        Resource = var.sqs_queue_arns
      }
    ]
  })
}
