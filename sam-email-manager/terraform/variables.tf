variable "logger_level" {
  description = "Nivel de logging para los recursos"
  type        = string
  default     = "INFO"

  validation {
    condition     = contains(["CRITICAL", "FATAL", "ERROR", "WARNING", "WARN", "INFO", "DEBUG", "NOTSET"], var.logger_level)
    error_message = "logger_level must be one of the values : CRITICAL, FATAL, ERROR, WARNING, WARN, INFO, DEBUG, NOTSET."
  }
}

variable "aws_region" {
  description = "AWS region to deploy resources"
  type        = string
}

variable "google_region" {
  description = "Google Cloud region to deploy resources"
  type        = string
}

variable "google_project_id" {
  description = "Google Cloud project ID"
  type        = string
}

variable "environment" {
  description = "Deployment environment (e.g., dev, staging, prod)"
  type        = string
  
}