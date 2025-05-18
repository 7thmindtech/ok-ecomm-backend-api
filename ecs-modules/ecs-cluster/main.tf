resource "aws_ecs_cluster" "ok_ecs_cluster" {
  name = var.cluster_name
  setting {
    name  = "containerInsights"
    value = "enabled"
  }
  configuration {
    execute_command_configuration {
      kms_key_id = var.kms_id
      logging    = "OVERRIDE"

      log_configuration {
        cloud_watch_encryption_enabled = true
        cloud_watch_log_group_name     = var.log_groud_name
      }
    }
  }
  tags = var.tags
}

resource "aws_ecs_cluster_capacity_providers" "ok_ecs_clust_cap_prov" {
  cluster_name = aws_ecs_cluster.ok_ecs_cluster.name

  capacity_providers = ["FARGATE"]

  default_capacity_provider_strategy {
    base              = 1
    weight            = 100
    capacity_provider = "FARGATE"
  }
}


