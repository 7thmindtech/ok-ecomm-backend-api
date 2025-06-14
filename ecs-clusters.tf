module "ok_backend_ecs_cluster" {
    source = "./ecs-modules/ecs-cluster"
    env = var.env
    cust_name = var.cust_name
    cluster_name = "${var.cust_name}-${var.ecs_cluster_name}-${var.env}-ecs-cluster"
    kms_id = aws_kms_key.ok_cluster_key.arn
    log_groud_name = aws_cloudwatch_log_group.ok_cluster_log_grp.name
    tags = merge(local.tags, tomap({ "Name" = "${var.cust_name}-${var.ecs_cluster_name}-${var.env}-cluster" }))
}