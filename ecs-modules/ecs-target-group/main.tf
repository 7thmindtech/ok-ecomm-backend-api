
resource "aws_lb_target_group" "ok_ecs_tg" {
  name        = "${var.cust_name}-${var.ecs_family}-${var.env}-${var.stage_name}-${var.deployment_type}-tg"
  port        = 8080
  protocol    = "HTTP"
  target_type = "ip"
  vpc_id      = var.vpc_id
  health_check {
    path                = var.health_path
    port = "8080"
    protocol            = "HTTP"
    healthy_threshold   = 5
    unhealthy_threshold = 2
    interval            = 30
    timeout             = 29
    matcher             = "200"
  }
  tags = var.tags
}

# Listen on SSL port 443
#
# resource "aws_lb_listener" "pd_app_listner_443" {
#   load_balancer_arn = aws_lb.aws-alb.arn
#   port              = "443"
#   protocol          = "HTTPS"
#   ssl_policy        = "ELBSecurityPolicy-TLS-1-2-2017-01"
#   certificate_arn   = data.aws_acm_certificate.this.arn

#   default_action {
#     type             = "forward"
#     target_group_arn = aws_lb_target_group.target-group.arn
#   }

#   tags = merge(local.tags, tomap({ "Name" = "${var.cust_name}-app-listner-443" }))
# }

# data "aws_acm_certificate" "this" {
#   domain      = var.app_custom_domain_name
#   types       = ["AMAZON_ISSUED"]
#   most_recent = true
# }

