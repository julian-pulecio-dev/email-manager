resource "aws_lambda_layer_version" "layer" {
  filename   = "../dependencies/${var.name}.zip"
  layer_name = var.name

  compatible_runtimes = ["python3.12"]
}