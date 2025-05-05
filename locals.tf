data "aws_caller_identity" "current" {}


locals {
  tags = {
    Env        = var.env
    Project    = var.project
    Owner      = var.owner
    Repository = var.repository
    Script     = "terraform"
  }

  account_id = data.aws_caller_identity.current.account_id
  vpc_id      = data.terraform_remote_state.infra.outputs.vpc_id
  pub_sub_sg = data.terraform_remote_state.infra.outputs.pub_sub_sg
  ecs_sub_sg = data.terraform_remote_state.infra.outputs.ecs_sub_sg
  alb_sg     = data.terraform_remote_state.infra.outputs.alb_sg
  alb_access_log_bucket = data.terraform_remote_state.infra.outputs.alb_access_log_bucket

  private_subnet_a = data.terraform_remote_state.infra.outputs.app_priv_sub_1
  private_subnet_b = data.terraform_remote_state.infra.outputs.app_priv_sub_2
  private_subnet_c = data.terraform_remote_state.infra.outputs.app_priv_sub_3
  private_subnet_ids = [local.private_subnet_a,local.private_subnet_b,local.private_subnet_c]

  db_subnet_a = data.terraform_remote_state.infra.outputs.db_priv_sub_1
  db_subnet_b = data.terraform_remote_state.infra.outputs.db_priv_sub_2
  db_subnet_c = data.terraform_remote_state.infra.outputs.db_priv_sub_3
  db_subnet_ids = [local.db_subnet_a,local.db_subnet_b,local.db_subnet_c]

  pub_sub_a = data.terraform_remote_state.infra.outputs.pub_sub_1
  pub_sub_b = data.terraform_remote_state.infra.outputs.pub_sub_2
  pub_sub_c = data.terraform_remote_state.infra.outputs.pub_sub_3
  public_subnet_ids = [local.pub_sub_a,local.pub_sub_b,local.pub_sub_c]

}
# ##############