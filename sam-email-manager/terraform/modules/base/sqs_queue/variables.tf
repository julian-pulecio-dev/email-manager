variable "queue_name" {
  description = "Nombre de la cola SQS principal"
  type        = string
}

variable "delay_seconds" {
  description = "Tiempo de retraso en segundos para los mensajes"
  type        = number
  default     = 0
  validation {
    condition     = var.delay_seconds >= 0 && var.delay_seconds <= 900
    error_message = "delay_seconds debe estar entre 0 y 900 segundos."
  }
}

variable "max_message_size" {
  description = "Tamaño máximo del mensaje en bytes"
  type        = number
  default     = 262144  # 256 KB por defecto
  validation {
    condition     = var.max_message_size >= 1024 && var.max_message_size <= 262144
    error_message = "max_message_size debe estar entre 1 KB y 256 KB."
  }
}

variable "message_retention_seconds" {
  description = "Tiempo de retención del mensaje en segundos"
  type        = number
  default     = 345600  # 4 días por defecto
  validation {
    condition     = var.message_retention_seconds >= 60 && var.message_retention_seconds <= 1209600
    error_message = "message_retention_seconds debe estar entre 60 y 1209600 segundos."
  }
}

variable "receive_wait_time_seconds" {
  description = "Tiempo de espera para recibir mensajes (long polling)"
  type        = number
  default     = 0
  validation {
    condition     = var.receive_wait_time_seconds >= 0 && var.receive_wait_time_seconds <= 20
    error_message = "receive_wait_time_seconds debe estar entre 0 y 20 segundos."
  }
}

variable "dead_letter_queue_arn" {
  description = "ARN de la cola de Dead Letter"
  type        = string
  default     = null
}

variable "max_receive_count" {
  description = "Número máximo de intentos antes de enviar a la DLQ"
  type        = number
  default     = 5
  validation {
    condition     = var.max_receive_count > 0
    error_message = "max_receive_count debe ser mayor a 0."
  }
}


variable "trigger_lambda_arn" {
  description = "ARN de la función Lambda que será activada por la cola SQS"
  type        = string
  default     = null
}

variable "create_trigger" {
  type    = bool
  default = false
}

variable "visibility_timeout_seconds" {
  description = "Tiempo de visibilidad en segundos para los mensajes"
  type        = number
  default     = 30
  validation {
    condition     = var.visibility_timeout_seconds >= 0 && var.visibility_timeout_seconds <= 43200
    error_message = "visibility_timeout_seconds debe estar entre 0 y 43200 segundos."
  }
  
}