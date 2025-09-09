variable "dynamo_db_tables_arns" {
  description = "List of DynamoDB table ARNs that the role can access"
  type        = list(string)
  default     = []
}