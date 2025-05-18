
/* auth target group */
module "ok_ecomm_backend_tg_blue" {
    source = "./ecs-modules/ecs-target-group"
    env = var.env
    cust_name = var.cust_name
    ecs_family = var.ecs_family
    stage_name = var.stage_name
    vpc_id = data.terraform_remote_state.infra.outputs.vpc_id
    health_path = "/docs"
    ecs_service_id = module.ok_ecomm_backend_taskdef.task_arn
    deployment_type = "blue"
    tags = merge(local.tags, tomap({ "Name" = "${var.cust_name}-${var.ecs_family}-${var.env}-${var.stage_name}-tg-blue" }))
}

/* auth target group */
module "ok_ecomm_backend_tg_green" {
    source = "./ecs-modules/ecs-target-group"
    env = var.env
    cust_name = var.cust_name
    ecs_family = var.ecs_family
    stage_name = var.stage_name
    vpc_id = data.terraform_remote_state.infra.outputs.vpc_id
    health_path = "/docs"
    ecs_service_id = module.ok_ecomm_backend_taskdef.task_arn
    deployment_type = "green"
    tags = merge(local.tags, tomap({ "Name" = "${var.cust_name}-${var.ecs_family}-${var.env}-${var.stage_name}-tg-green" }))
}
