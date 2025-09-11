resource "aws_iam_policy" "cognito_policy" {
  name        = "lambda_cognito_policy"
  description = "Allow Lambda to access Cognito User Pools"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "cognito-idp:GetUser",
          "cognito-idp:ListUsers",
          "cognito-idp:AdminGetUser",
          "cognito-idp:AdminUpdateUserAttributes"
        ]
        Resource = var.cognito_user_pools_arns
      }
    ]
  })
}
