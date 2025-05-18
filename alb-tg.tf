resource "aws_lb_target_group" "ok-ecomm-tg" {
  name        = "${var.cust_name}-ecomm-backend-${var.env}-tg"
  port        = 8080
  protocol    = "HTTP" # Change to HTTPS when certificate is available
  target_type = "ip"
  vpc_id      = local.vpc_id

health_check {
    path                = "/docs"
    port                = "8080"
    protocol            = "HTTP"
    healthy_threshold   = 5
    unhealthy_threshold = 2
    interval            = 240
    timeout             = 120
    matcher             = "200"
  }
  tags = merge(local.tags, tomap({ "Name" = "${var.cust_name}-ecomm-${var.env}-tg" }))

}
