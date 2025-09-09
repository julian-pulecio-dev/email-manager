variable "api_id" {
  description = "The ID of the API Gateway"
  type        = string
}

variable "resource_id" {
  description = "The parent resource ID of the API Gateway"
  type        = string
}

variable "resource_path" {
  description = "The path of the resource"
  type        = string
}

variable "path_part" {
  description = "The path part for the resource"
  type        = string

}

variable "authorization_type" {
  description = "The type of authorization"
  type        = string
}

variable "authorizer_id" {
  description = "The ID of the Cognito User Pool Authorizer"
  type        = string

}

variable "lambda_name" {
  description = "The name of the Lambda function"
  type        = string
}

variable "lambda_arn" {
  description = "The ARN of the Lambda function"
  type        = string

}

variable "http_method" {
  description = "The HTTP method (e.g., GET, POST)"
  type        = string
}

variable "unique_key" {
  type        = string
  description = "Unique identifier for this module instance"
}