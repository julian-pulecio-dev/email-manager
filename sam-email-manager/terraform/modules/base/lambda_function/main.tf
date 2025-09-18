data "archive_file" "lambda_zip" {
  type        = "zip"
  source_dir  = "../lambdas"
  output_path = "${path.module}/lambda.zip"
}

# Rol de ejecución de Lambda
resource "aws_iam_role" "lambda_execution_role" {
  name_prefix = "${var.name}_exec_role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_policy" "cloudwatch_policy" {
  name_prefix = "${var.name}_cloudwatch_policy"
  description = "Allow Lambda to write logs to CloudWatch"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "cloudwatch_attach" {
  role       = aws_iam_role.lambda_execution_role.name
  policy_arn = aws_iam_policy.cloudwatch_policy.arn
}

resource "aws_iam_role_policy_attachment" "extra_policies" {
  for_each   = { for idx, arn in var.extra_policy_arns : idx => arn }
  role       = aws_iam_role.lambda_execution_role.name
  policy_arn = each.value
}

resource "aws_lambda_function" "lambda" {
  function_name    = var.name
  role             = aws_iam_role.lambda_execution_role.arn
  handler          = var.handler
  runtime          = "python3.11"
  timeout          = 600
  filename         = data.archive_file.lambda_zip.output_path
  layers           = var.layers
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256
  environment {
    variables = var.env_vars
  }
}
