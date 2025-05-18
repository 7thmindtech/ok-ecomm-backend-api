
output "alb_arn" {
  description = "Loadbalancer arn"
  value = aws_lb.ok-alb.arn
}

output "ecs_cw_log_group_name" {
  description = "ECS Cloudwatch log group name"
  value = aws_cloudwatch_log_group.ok_cluster_log_grp.name
}

output "ok_cluster_key_arn" {
  description = "ECS KMS key ARN"
  value = aws_kms_key.ok_cluster_key.arn
  
}

output "ok_codedeploy_app_name" {
  description = "CodeDeploy application name"
  value = aws_codedeploy_app.ok-codedeploy-app.name
  
}

output "ok_codedeploy_deployment_group_name" {
  description = "CodeDeploy deployment group name"
  value = aws_codedeploy_deployment_group.ok-codedeploy-deployment-group.deployment_group_name
  
}

