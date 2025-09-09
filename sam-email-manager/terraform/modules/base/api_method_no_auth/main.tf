data "aws_region" "current" {}
data "aws_caller_identity" "current" {}

resource "aws_api_gateway_method" "method" {
  for_each      = { for key, value in { "${var.unique_key}-${var.http_method}" = var.http_method } : key => value }
  rest_api_id   = var.api_id
  resource_id   = var.resource_id
  http_method   = each.value
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "integration" {
  for_each                = aws_api_gateway_method.method
  rest_api_id             = var.api_id
  resource_id             = var.resource_id
  http_method             = each.value.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = "arn:aws:apigateway:${data.aws_region.current.id}:lambda:path/2015-03-31/functions/${var.lambda_arn}/invocations"
}

resource "aws_lambda_permission" "apigw_lambda" {
  for_each      = aws_api_gateway_method.method
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = var.lambda_name
  principal     = "apigateway.amazonaws.com"

  # More: http://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-control-access-using-iam-policies-to-invoke-api.html
  source_arn = "arn:aws:execute-api:${data.aws_region.current.id}:${data.aws_caller_identity.current.account_id}:${var.api_id}/*/${each.value.http_method}${var.resource_path}"
}
