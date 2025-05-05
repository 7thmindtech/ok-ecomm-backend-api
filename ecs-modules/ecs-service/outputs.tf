output "ecs_service_id" {
  description = "Id of the ECS service"
  value       = aws_ecs_service.ecs_service.id
}

output "ecs_service_name" {
  description = "Name of the ECS service"
  value       = aws_ecs_service.ecs_service.name
}
output "ecs_service_desired_count" {
  description = "desired count of the ECS service"
  value       = aws_ecs_service.ecs_service.desired_count
}
output "ecs_service_cluster" {
  description = "cluster arn of the ECS service"
  value       = aws_ecs_service.ecs_service.cluster
}
