resource "aws_cognito_user_pool" "pool" {
  name = var.name
}

resource "aws_cognito_identity_provider" "google_provider" {
  user_pool_id  = aws_cognito_user_pool.pool.id
  provider_name = "Google"
  provider_type = "Google"

  provider_details = {
    authorize_scopes = "email"
    client_id        = var.google_client_id
    client_secret    = var.google_client_secret
  }

  attribute_mapping = {
    email    = "email"
    username = "sub"
  }

  depends_on = [
    aws_cognito_user_pool.pool
  ]
}

resource "aws_cognito_user_pool_client" "client" {
  name                                 = "${var.name}_client"
  user_pool_id                         = aws_cognito_user_pool.pool.id
  generate_secret                      = false
  allowed_oauth_flows                  = ["code"]
  allowed_oauth_scopes                 = ["email", "openid", "profile"]
  allowed_oauth_flows_user_pool_client = true
  callback_urls                        = ["http://localhost:5173/social-login-confirm-code"]
  logout_urls                          = ["http://localhost:5173/social-login-logout"]
  supported_identity_providers         = ["Google"]
  read_attributes                      = ["email", "name"]
  write_attributes                     = ["email", "name"]
  enable_token_revocation              = true
  refresh_token_validity               = 30
  depends_on = [
    aws_cognito_identity_provider.google_provider
  ]
}

resource "aws_cognito_user_pool_domain" "domain" {
  domain       = var.domain_name
  user_pool_id = aws_cognito_user_pool.pool.id
  depends_on = [
    aws_cognito_user_pool.pool
  ]
}


resource "aws_api_gateway_authorizer" "cognito_authorizer" {
  name            = "cognito"
  rest_api_id     = var.api_id
  type            = "COGNITO_USER_POOLS"
  provider_arns   = [aws_cognito_user_pool.pool.arn]
  identity_source = "method.request.header.Authorization"
}