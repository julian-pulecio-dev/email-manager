output "arn" {
  value = aws_lambda_function.lambda.arn
}

output "name" {
  value = aws_lambda_function.lambda.function_name
}

output "role_arn" {
  value = aws_iam_role.lambda_execution_role.arn
}