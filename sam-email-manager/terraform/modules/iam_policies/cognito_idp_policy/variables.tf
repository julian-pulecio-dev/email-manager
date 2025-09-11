variable "cognito_user_pools_arns" {
  description = "List of Cognito User Pool ARNs that the role can access"
  type        = list(string)
  default     = []
}