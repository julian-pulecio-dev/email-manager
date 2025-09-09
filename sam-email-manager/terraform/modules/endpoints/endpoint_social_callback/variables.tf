variable "api_id" {
  description = "The ID of the API Gateway"
  type        = string
}

variable "parent_resource_id" {
  description = "The ID of the parent resource"
  type        = string
}

variable "layers" {
  description = "The Lambda layers to include"
  type        = list(string)
}

variable "env_vars" {
  description = "The environment variables for the Lambda function"
  type        = map(string)
}

variable "extra_policy_arns" {
  type    = list(string)
  default = []
}