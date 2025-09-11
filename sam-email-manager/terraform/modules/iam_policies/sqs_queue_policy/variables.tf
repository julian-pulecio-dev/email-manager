variable "sqs_queue_name" {
  description = "Nombre de la cola SQS principal"
  type        = string
}

variable "sqs_queue_arns" {
  description = "ARNs de las colas SQS"
  type        = list(string)
  
}