output "ecs_target_group_id" {
  description = "Id of the ECS service"
  value       = aws_lb_target_group.ok_ecs_tg.id
}

output "ecs_target_group_name" {
  description = "Id of the ECS service"
  value       = aws_lb_target_group.ok_ecs_tg.name
}
output "ecs_target_group_arn" {
  description = "Id of the ECS service"
  value       = aws_lb_target_group.ok_ecs_tg.arn
}