resource "aws_ecs_task_definition" "ok_ecs_task" {
  family                   = "${var.cust_name}-${var.ecs_family}-${var.env}-ecs-task"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = var.taskcpu
  memory                   = var.taskmem
  execution_role_arn       = aws_iam_role.ecs_task_role.arn
  task_role_arn            = aws_iam_role.ecs_task_role.arn
  container_definitions    = var.container_definitions
  tags = var.tags
}

resource "aws_iam_role" "ecs_task_role" {
  name = "${var.ecs_family}-${var.env}-ecs-role"

  assume_role_policy = <<EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Action": "sts:AssumeRole",
            "Principal": {
                "Service": "ecs-tasks.amazonaws.com" 
            },
            "Effect": "Allow",
            "Sid": "ECSAssumeRole"
        }
    ]
}
EOF

    tags   = var.role_tags
}


resource "aws_iam_role_policy" "custom-policy" {
  name   = "${var.ecs_family}-${var.env}-ecs-role-policy"
  role   = aws_iam_role.ecs_task_role.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "s3:GetObject",
          "s3:PutObject"
        ]
        Effect   = "Allow"
        Resource = "*"
      },
      {
        Action = [
          "application-autoscaling:*",
          "cloudwatch:*",
          "ecs:*",
          "elasticloadbalancing:*",
          "secretsmanager:*",
          "logs:*",
          "ssm:*",
          "iam:PassRole"
        ]
        Effect   = "Allow"
        Resource = "*"
      }
    ]
  })
}


resource "aws_iam_role_policy_attachment" "AmazonSSMFullAccess" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMFullAccess" 
  role       = aws_iam_role.ecs_task_role.name
}

resource "aws_iam_role_policy_attachment" "AmazonECSTaskExecutionRolePolicy" {
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy" 
  role       = aws_iam_role.ecs_task_role.name
}

resource "aws_iam_role_policy_attachment" "CloudWatchFullAccess" {
  policy_arn = "arn:aws:iam::aws:policy/CloudWatchFullAccess" 
  role       = aws_iam_role.ecs_task_role.name
}