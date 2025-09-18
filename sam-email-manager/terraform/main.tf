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

provider "aws" {
  region = var.aws_region
}

provider "google" {
  project = var.google_project_id
  region  = var.google_region
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

module "cognito_idp_policy" {
  source = "./modules/iam_policies/cognito_idp_policy"
  cognito_user_pools_arns = [
    module.cognito_auth.pool_arn
  ]
}

module "sqs_queue_policy" {
  source = "./modules/iam_policies/sqs_queue_policy"
  sqs_queue_name = "email-manager-queue"
  sqs_queue_arns = [
    module.sqs_queue.arn
  ]
}

module "lambda_layer" {
  source = "./modules/base/lambda_layer"
  name   = "core"
}

module "event_bridge" {
  source = "./modules/event_bridge_scheduler"
  schedule_expression = "rate(1 hours)"
  schedule_name = "schedule_user_dispatcher"
  schedule_handler = "handlers/event_bridge_scheduler/schedule_user_processor.lambda_handler"
  lambda_layers_arns = [module.lambda_layer.arn]
  env_vars = {
    EMAIL_MANAGER_AUTH_USER_POOL_ID : module.cognito_auth.pool_id
    SQS_QUEUE_URL : module.sqs_queue.url
    LOGGER_LEVEL : var.logger_level
  }
  extra_policy_arns = [module.cognito_idp_policy.arn, module.sqs_queue_policy.arn]
}

module "endpoint_social_callback" {
  source             = "./modules/endpoints/endpoint_social_callback"
  api_id             = module.api.id
  parent_resource_id = module.api.root_resource_id
  layers             = [module.lambda_layer.arn]
  env_vars = {
    EMAIL_MANAGER_AUTH_USER_POOL_CLIENT_ID : module.cognito_auth.client_id
    EMAIL_MANAGER_AUTH_USER_POOL_ID : module.cognito_auth.pool_id
    EMAIL_MANAGER_AUTH_USER_POOL_DOMAIN : module.cognito_auth.domain
    CALLBACK_URL : "http://localhost:5173/social-login-confirm-code"
    LOGGER_LEVEL : var.logger_level
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
    GMAIL_WATCH_PUB_SUB_NAME : "projects/${var.google_project_id}/topics/${module.pub_sub.topic_name}"
    GMAIL_HISTORY_ID_TABLE_NAME : module.dynamodb_gmail_history_id.name
    EMAIL_MANAGER_AUTH_USER_POOL_ID : module.cognito_auth.pool_id
    EMAIL_MANAGER_AUTH_USER_POOL_CLIENT_ID : module.cognito_auth.client_id
    LOGGER_LEVEL : var.logger_level
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
    EMAIL_MANAGER_AUTH_USER_POOL_ID : module.cognito_auth.pool_id
    EMAIL_MANAGER_AUTH_USER_POOL_CLIENT_ID : module.cognito_auth.client_id
    LOGGER_LEVEL : var.logger_level
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
    EMAIL_MANAGER_AUTH_USER_POOL_ID : module.cognito_auth.pool_id
    EMAIL_MANAGER_AUTH_USER_POOL_CLIENT_ID : module.cognito_auth.client_id
    GMAIL_HISTORY_ID_TABLE_NAME: module.dynamodb_gmail_history_id.name
    GMAIL_CUSTOM_LABELS_TABLE_NAME: module.dynamodb_labels_table.name
    LOGGER_LEVEL : var.logger_level
  }
  authorizer_id     = module.cognito_auth.cognito_authorizer_id
  extra_policy_arns = [module.dynamo_db_policy.arn]
}

module "lambda_process_email" {
  source = "./modules/base/lambda_function"
  name   = "process_email"
  handler = "handlers/email/process_email.lambda_handler"
  env_vars = {
    GOOGLE_CLIENT_ID: module.secret_google_credentials.decoded_secret["email_manager_google_client_id"]
    GOOGLE_CLIENT_SECRET: module.secret_google_credentials.decoded_secret["email_manager_google_client_secret"]
    GOOGLE_ACCOUNT_CREDENTIALS: jsonencode(module.secret_google_account.decoded_secret)
    GOOGLE_OAUTH_ACCESS_TOKENS_TABLE_NAME: module.dynamodb_user_tokens.name
    EMAIL_MANAGER_AUTH_USER_POOL_ID : module.cognito_auth.pool_id
    EMAIL_MANAGER_AUTH_USER_POOL_CLIENT_ID : module.cognito_auth.client_id
    GMAIL_HISTORY_ID_TABLE_NAME: module.dynamodb_gmail_history_id.name
    GMAIL_CUSTOM_LABELS_TABLE_NAME: module.dynamodb_labels_table.name
    LOGGER_LEVEL: var.logger_level
  }
  layers = [module.lambda_layer.arn]
  extra_policy_arns = [module.dynamo_db_policy.arn, module.sqs_queue_policy.arn]
}

module "sqs_dead_letter_queue" {
  source = "./modules/base/sqs_queue"
  queue_name =  "email-manager-dead-letter-queue"
  visibility_timeout_seconds = 300
}

module "sqs_queue" {
  source = "./modules/base/sqs_queue"
  queue_name =  "email-manager-queue"
  create_trigger = true
  trigger_lambda_arn = module.lambda_process_email.arn
  visibility_timeout_seconds = 600
  dead_letter_queue_arn = module.sqs_dead_letter_queue.arn
}