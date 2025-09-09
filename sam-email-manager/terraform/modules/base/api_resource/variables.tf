variable "api_id" {
  description = "The ID of the API Gateway"
  type        = string
}

variable "parent_resource_id" {
  description = "The parent resource ID of the API Gateway"
  type        = string
}

variable "path_part" {
  description = "The path part for the resource"
  type        = string

}

variable "allow_origin" {
  description = "The allowed origin for CORS"
  type        = string
}

variable "allowed_methods" {
  description = "The allowed methods for CORS"
  type        = list(string)
}

variable "allowed_headers" {
  description = "The allowed headers for CORS"
  type        = list(string)
}