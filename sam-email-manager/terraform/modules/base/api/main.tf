# API Gateway
resource "aws_api_gateway_rest_api" "api" {
  name = var.name
  binary_media_types = [
    "multipart/form-data"
  ]
}
