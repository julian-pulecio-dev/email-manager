# Variables
terraform {
  required_providers {
    google = {
      source = "hashicorp/google"
    }
    aws = {
      source = "hashicorp/aws"
    }
  }
}

provider "google" {
  project = "email-manager-467721"
  region  = "us-central1"
}

provider "aws" {
  region = "us-east-1"

}

data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

module "secret_google_credentials" {
  source      = "./modules/base/secret_manager"
  secret_name = "dev/email_manager_google_credentials"
}

module "secret_google_account" {
  source      = "./modules/base/secret_manager"
  secret_name = "dev/email_manager_account_credentials"
}

module "api" {
  source = "./modules/base/api"
  name   = "email_manager"
}

module "cognito_auth" {
  source               = "./modules/base/cognito_auth"
  name                 = "email_manager_pool"
  api_id               = module.api.id
  domain_name          = "email-manager-auth-domain"
  google_client_id     = module.secret_google_credentials.decoded_secret["email_manager_google_client_id"]
  google_client_secret = module.secret_google_credentials.decoded_secret["email_manager_google_client_secret"]
}

module "pub_sub" {
  source               = "./modules/base/pub_sub"
  topic_name           = "my-topic"
  subscription_name    = "my-subscription"
  api_gateway_endpoint = ""
  push_service_account = ""
}

module "dynamodb_user_tokens" {
  source   = "./modules/base/dynamo_db"
  name     = "UserTokens"
  hash_key = "email"
  attributes = {
    email = "S"
  }
}

module "dynamodb_gmail_history_id" {
  source   = "./modules/base/dynamo_db"
  name     = "GmailHistoryId"
  hash_key = "email"
  attributes = {
    email = "S"
  }
}

module "dynamodb_labels_table" {
  source = "./modules/base/dynamo_db"
  name      = "CustomLabels"
  hash_key  = "email"
  range_key = "title"

  attributes = {
    email = "S"
    title = "S"
  }
}


module "dynamo_db_policy" {
  source = "./modules/iam_policies/dynamo_db_policy"
  dynamo_db_tables_arns = [
    module.dynamodb_user_tokens.arn,
    module.dynamodb_gmail_history_id.arn,
    module.dynamodb_labels_table.arn
  ]
}

module "lambda_layer" {
  source = "./modules/base/lambda_layer"
  name   = "core"
}


module "endpoint_social_callback" {
  source             = "./modules/endpoints/endpoint_social_callback"
  api_id             = module.api.id
  parent_resource_id = module.api.root_resource_id
  layers             = [module.lambda_layer.arn]
  env_vars = {
    EMAIL_MANAGER_AUTH_USER_POOL_CLIENT_ID : module.cognito_auth.client_id
    EMAIL_MANAGER_AUTH_USER_POOL_DOMAIN : module.cognito_auth.domain
    CALLBACK_URL : "http://localhost:5173/social-login-confirm-code"
  }
}



module "endpoint_google_access_tokens" {
  source             = "./modules/endpoints/endpoint_google_access_tokens"
  api_id             = module.api.id
  parent_resource_id = module.api.root_resource_id
  layers             = [module.lambda_layer.arn]
  env_vars = {
    GOOGLE_CLIENT_ID : module.secret_google_credentials.decoded_secret["email_manager_google_client_id"]
    GOOGLE_CLIENT_SECRET : module.secret_google_credentials.decoded_secret["email_manager_google_client_secret"]
    GOOGLE_OAUTH_ACCESS_TOKENS_TABLE_NAME : module.dynamodb_user_tokens.name
    GMAIL_WATCH_PUB_SUB_NAME : "projects/email-manager-467721/topics/${module.pub_sub.topic_name}"
    GMAIL_HISTORY_ID_TABLE_NAME : module.dynamodb_gmail_history_id.name
  }
  authorizer_id     = module.cognito_auth.cognito_authorizer_id
  extra_policy_arns = [module.dynamo_db_policy.arn]
}


module "endpoint_send_email" {
  source             = "./modules/endpoints/endpoint_send_email"
  api_id             = module.api.id
  parent_resource_id = module.api.root_resource_id
  layers             = [module.lambda_layer.arn]
  env_vars = {
    GOOGLE_CLIENT_ID: module.secret_google_credentials.decoded_secret["email_manager_google_client_id"]
    GOOGLE_CLIENT_SECRET: module.secret_google_credentials.decoded_secret["email_manager_google_client_secret"]
    GOOGLE_ACCOUNT_CREDENTIALS: jsonencode(module.secret_google_account.decoded_secret)
    GOOGLE_OAUTH_ACCESS_TOKENS_TABLE_NAME: module.dynamodb_user_tokens.name
  }
  authorizer_id     = module.cognito_auth.cognito_authorizer_id
  extra_policy_arns = [module.dynamo_db_policy.arn]
}

module "endpoint_label" {
  source             = "./modules/endpoints/endpoint_label"
  api_id             = module.api.id
  parent_resource_id = module.api.root_resource_id
  layers             = [module.lambda_layer.arn]
  env_vars = {
    GOOGLE_CLIENT_ID: module.secret_google_credentials.decoded_secret["email_manager_google_client_id"]
    GOOGLE_CLIENT_SECRET: module.secret_google_credentials.decoded_secret["email_manager_google_client_secret"]
    GOOGLE_ACCOUNT_CREDENTIALS: jsonencode(module.secret_google_account.decoded_secret)
    GOOGLE_OAUTH_ACCESS_TOKENS_TABLE_NAME: module.dynamodb_user_tokens.name
    GMAIL_HISTORY_ID_TABLE_NAME: module.dynamodb_gmail_history_id.name
    GMAIL_CUSTOM_LABELS_TABLE_NAME: module.dynamodb_labels_table.name
  }
  authorizer_id     = module.cognito_auth.cognito_authorizer_id
  extra_policy_arns = [module.dynamo_db_policy.arn]
}

module "endpoint_process_email" {
  source             = "./modules/endpoints/endpoint_process_email"
  api_id             = module.api.id
  parent_resource_id = module.api.root_resource_id
  layers             = [module.lambda_layer.arn]
  env_vars = {
    GOOGLE_CLIENT_ID: module.secret_google_credentials.decoded_secret["email_manager_google_client_id"]
    GOOGLE_CLIENT_SECRET: module.secret_google_credentials.decoded_secret["email_manager_google_client_secret"]
    GOOGLE_ACCOUNT_CREDENTIALS: jsonencode(module.secret_google_account.decoded_secret)
    GOOGLE_OAUTH_ACCESS_TOKENS_TABLE_NAME: module.dynamodb_user_tokens.name
    GMAIL_HISTORY_ID_TABLE_NAME: module.dynamodb_gmail_history_id.name
    GMAIL_CUSTOM_LABELS_TABLE_NAME: module.dynamodb_labels_table.name
  }
  authorizer_id     = module.cognito_auth.cognito_authorizer_id
  extra_policy_arns = [module.dynamo_db_policy.arn]
}