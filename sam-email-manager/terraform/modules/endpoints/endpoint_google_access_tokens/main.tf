module "api_resource" {
  source             = "../../base/api_resource"
  api_id             = var.api_id
  parent_resource_id = var.parent_resource_id
  path_part          = "google_access_tokens"
  allow_origin       = "*"
  allowed_methods    = ["GET", "POST", "OPTIONS"]
  allowed_headers    = ["Content-Type", "X-Amz-Date", "Authorization", "X-Api-Key", "X-Amz-Security-Token"]
}

module "lambda_function" {
  source            = "../../base/lambda_function"
  name              = "google_access_tokens"
  handler           = "handlers/auth/google_access_tokens.lambda_handler"
  layers            = var.layers
  env_vars          = var.env_vars
  extra_policy_arns = var.extra_policy_arns
}

module "api_method_auth" {
  source             = "../../base/api_method_auth"
  api_id             = var.api_id
  unique_key         = "email_manager_google_access_tokens"
  resource_id        = module.api_resource.id
  resource_path      = module.api_resource.path
  path_part          = ""
  authorization_type = "COGNITO_USER_POOLS"
  authorizer_id      = var.authorizer_id
  http_method        = "POST"
  lambda_name        = module.lambda_function.name
  lambda_arn         = module.lambda_function.arn
}