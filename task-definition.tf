
module "ok_ecomm_backend_taskdef" {
    source = "./ecs-modules/ecs-taskdef"
    env = var.env
    cust_name = var.cust_name
    ecs_family = var.ecs_family
    stage_name = var.stage_name
    taskcpu = 512
    taskmem = 1024  #replace cont def image with "${var.account_id}.dkr.ecr.eu-west-1.amazonaws.com/ok-ecr-registry:${var.ecs_family}-${var.env}-${var.stage_name}" when u build image. Also remember to change the port
    tags = merge(local.tags, tomap({ "Name" = "${var.cust_name}-${var.ecs_family}-${var.env}"}))
    role_tags = merge(local.tags, tomap({ "Name" = "${var.cust_name}-${var.ecs_family}-${var.env}-role" }))
    container_definitions = jsonencode([
        {
            "name" = "${var.cust_name}-${var.ecs_family}-${var.env}-${var.stage_name}",
            "image" = "nginx:latest",
            "essential" = true,
            "portMappings" = [
                {
                    "protocol"      = "tcp",
                    "containerPort" = 80,
                    "hostPort"      = 80
                }
            ],
            "secrets" = local.ok_ecomm_backend_secrets,
            "logConfiguration" = {
                "logDriver" = "awslogs",
                "options"   = {
                    "awslogs-create-group"   = "true",
                    "awslogs-group"          = "ecs/fargate/service/${var.env}/${var.ecs_family}",
                    "awslogs-region"         = "eu-west-1",
                    "awslogs-stream-prefix"  = "ecs"
                }
            }
        }
    ])

    custom_policy_document = <<EOF
    {
    "Version": "2012-10-17",
    "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "s3:GetObject",
                    "s3:PutObject"
                ],
                "Resource": "*"
            },
            {
                "Effect": "Allow",
                "Action": [
                "application-autoscaling:*",
                "cloudwatch:*",
                "ecs:*"
                ],
                "Resource": "*"
            }
        ]
    }
    EOF
}
