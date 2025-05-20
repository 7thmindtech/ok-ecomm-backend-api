
/* def ECS service for auth api infra */
module "ok_ecomm_backend_serivce" {
    source = "./ecs-modules/ecs-service"
    env = var.env
    cust_name = var.cust_name
    serivce_name = var.ecs_cluster_name
    cluster_id = module.ok_backend_ecs_cluster.cluster_name
    task_definition_arn = module.ok_ecomm_backend_taskdef.task_arn
    desired_counts = 1
    enable_execute_command = true
    alb_target_group_arn = module.ok_ecomm_backend_tg_blue.ecs_target_group_arn
    subnet_ids = local.private_subnet_ids # to be changed to private endpoint
    security_groups = local.ecs_sub_sg # to be changed to private endpoint
    assign_public_ip = false
    container_name = module.ok_ecomm_backend_taskdef.container_name

    tags = merge(local.tags, tomap({ "Name" = "${var.cust_name}-${var.ecs_family}-ecs-service-${var.env}" }))
    depends_on = [module.ok_backend_ecs_cluster, module.ok_ecomm_backend_taskdef]
}
