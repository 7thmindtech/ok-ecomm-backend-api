
resource "aws_lb" "ok-alb" {
  name     = "${var.cust_name}-alb"
  internal = false

  security_groups = [
    aws_security_group.ok_alb_sg.id,
  ]

  subnets = aws_subnet.public_subnet[*].id
  idle_timeout = 120

  ip_address_type    = "ipv4"
  load_balancer_type = "application"

  access_logs {
    bucket = data.terraform_remote_state.infra.outputs.alb_access_log_bucket # This is the bucket name where the logs will be stored. It must match the bucket policy.
    prefix = "alb" # This is the prefix for the logs in the S3 bucket. It must match the prefix in the bucket policy. (i.e whatever you set after the bucket name, just befor 'AWSLogs')
    enabled = true
  }
  enable_deletion_protection = false

  tags = merge(local.tags, tomap({ "Name" = "${var.cust_name}-alb" }))
}
