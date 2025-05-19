
resource "aws_codedeploy_app" "ok-codedeploy-app" {
  name = "${var.cust_name}-${var.ecs_cluster_name}-${var.env}-codedeploy-app"
  compute_platform = "ECS"

  tags = merge(local.tags, tomap({ "Name" = "${var.cust_name}-${var.ecs_cluster_name}-${var.env}codedeploy-app" }))
  
}
resource "aws_codedeploy_deployment_group" "ok-codedeploy-deployment-group" {
  app_name = aws_codedeploy_app.ok-codedeploy-app.name
  deployment_group_name = "${var.cust_name}-${var.ecs_cluster_name}-${var.env}-codedeploy-deployment-group"
  service_role_arn = aws_iam_role.codedeploy_role.arn
  
  deployment_config_name = "CodeDeployDefault.ECSAllAtOnce"

  deployment_style {
    deployment_type = "BLUE_GREEN"
    deployment_option = "WITH_TRAFFIC_CONTROL"
  }
  
  ecs_service {
    cluster_name = "${var.cust_name}-${var.ecs_cluster_name}-${var.env}-ecs-cluster"
    service_name = module.ok_ecomm_backend_serivce.ecs_service_name
  }
  
  load_balancer_info {
    target_group_pair_info {
        target_group {
            name = module.ok_ecomm_backend_tg_blue.ecs_target_group_name
        }
        target_group {
            name = module.ok_ecomm_backend_tg_green.ecs_target_group_name
        }
        prod_traffic_route {
            listener_arns = [aws_lb_listener.alb-listner_80.arn]
        }
    }
  }

    blue_green_deployment_config {
        deployment_ready_option {
            action_on_timeout = "CONTINUE_DEPLOYMENT"
        }
        terminate_blue_instances_on_deployment_success {
            action = "TERMINATE"
            termination_wait_time_in_minutes = 5
        }
    }
    auto_rollback_configuration {
        enabled = true
        events  = ["DEPLOYMENT_FAILURE", "DEPLOYMENT_STOP_ON_ALARM"]
    }

    tags = merge(local.tags, tomap({ "Name" = "${var.cust_name}-${var.ecs_cluster_name}-${var.env}-codedeploy-deployment-group" }))
}


data "aws_iam_policy_document" "assume_role" {
  statement {
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["codedeploy.amazonaws.com"]
    }

    actions = ["sts:AssumeRole"]
  }
}

resource "aws_iam_role" "codedeploy_role" {
  name               = "${var.cust_name}-${var.ecs_cluster_name}-${var.env}-codedeploy-role"
  assume_role_policy = data.aws_iam_policy_document.assume_role.json
}

resource "aws_iam_role_policy_attachment" "AWSCodeDeployRole" {
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSCodeDeployRole"
  role       = aws_iam_role.codedeploy_role.name
}

resource "aws_iam_role_policy" "codedeploy_ecs_policy" {
  name   = "${var.cust_name}-${var.ecs_cluster_name}-${var.env}-codedeploy-ecs-policy"
  role   = aws_iam_role.codedeploy_role.id

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "ecs:DescribeServices",
          "ecs:DescribeTaskDefinition",
          "ecs:DescribeTasks",
          "ecs:ListTasks",
          "elasticloadbalancing:DescribeTargetGroups",
          "elasticloadbalancing:DescribeListeners",
          "elasticloadbalancing:DescribeLoadBalancers"
        ],
        Resource = "*"
      }
    ]
  })
}