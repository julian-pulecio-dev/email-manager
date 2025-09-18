resource "aws_sqs_queue" "terraform_queue" {
  name                      = var.queue_name
  delay_seconds             = var.delay_seconds
  visibility_timeout_seconds = var.visibility_timeout_seconds
  max_message_size          = var.max_message_size
  message_retention_seconds = var.message_retention_seconds
  receive_wait_time_seconds = var.receive_wait_time_seconds
  redrive_policy = var.dead_letter_queue_arn != null ? jsonencode({
    deadLetterTargetArn = var.dead_letter_queue_arn
    maxReceiveCount     = var.max_receive_count
  }) : null
}

resource "aws_lambda_event_source_mapping" "sqs_trigger" {
  count = var.create_trigger ? 1 : 0

  event_source_arn = aws_sqs_queue.terraform_queue.arn
  function_name    = var.trigger_lambda_arn
  batch_size       = 10
}