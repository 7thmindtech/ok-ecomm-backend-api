data "aws_secretsmanager_secret" "secret" {
  for_each = toset(var.secret_names)
  name     = "${var.env}-${each.key}"
}

locals {
  ok_ecomm_backend_secrets = [
    for secret_name in var.secret_names : {
      name      = secret_name
      valueFrom = data.aws_secretsmanager_secret.secret[secret_name].arn
    }
  ]
}