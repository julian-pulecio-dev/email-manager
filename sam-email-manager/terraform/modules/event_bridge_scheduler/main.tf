
module "lambda_scheduler" {
  source            = "../base/lambda_function"
  name              = var.schedule_name
  handler           = var.schedule_handler
  layers            = var.lambda_layers_arns
  env_vars          = var.env_vars
  extra_policy_arns = var.extra_policy_arns
}


resource "aws_iam_role" "scheduler_role" {
  name = "${var.schedule_name}-scheduler-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Effect = "Allow",
      Principal = {
        Service = "scheduler.amazonaws.com"
      },
      Action = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role_policy" "scheduler_policy" {
  name   = "${var.schedule_name}-scheduler-policy"
  role   = aws_iam_role.scheduler_role.id
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Effect = "Allow",
      Action = "lambda:InvokeFunction",
      Resource = module.lambda_scheduler.arn
    }]
  })
}



resource "aws_scheduler_schedule" "user_email_dispatcher" {
  name        = var.schedule_name
  description = "Schedule to trigger user processing"
  group_name  = "default"

  flexible_time_window {
    mode = "OFF"
  }

  schedule_expression = var.schedule_expression

  target {
    arn      = module.lambda_scheduler.arn
    role_arn = aws_iam_role.scheduler_role.arn
    input    = jsonencode({ triggered_by = "scheduler" })
  }
}
