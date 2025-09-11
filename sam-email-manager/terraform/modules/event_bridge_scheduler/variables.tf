variable "schedule_name" {
  description = "The name of the schedule"
  type        = string
}

variable "schedule_expression" {
  description = "The schedule expression (e.g., rate or cron)"
  type        = string
}

variable "schedule_handler" {
  description = "The ARN of the Lambda function to be triggered by the schedule"
  type = string
}

variable "lambda_layers_arns" {
  description = "The ARNs of the Lambda layers to be used by the scheduler function"
  type        = list(string)

}

variable "env_vars" {
  description = "Environment variables for the scheduler Lambda function"
  type        = map(string)
  default     = {}
}

variable "extra_policy_arns" {
  description = "Additional IAM policy ARNs to attach to the scheduler Lambda function"
  type        = list(string)
  default     = []
}