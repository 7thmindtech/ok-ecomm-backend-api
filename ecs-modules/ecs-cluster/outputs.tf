output "cluster_arn" {
    value       = aws_ecs_cluster.ok_ecs_cluster.arn
    description = "cluster arn"
}

output "cluster_name" {
    value       = aws_ecs_cluster.ok_ecs_cluster.id
    description = "cluster name"
}
