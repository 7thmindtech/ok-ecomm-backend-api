variable "env" {}
variable "cust_name" {}
variable "serivce_name" {}
variable "cluster_id" {}
variable "task_definition_arn" {}
variable "desired_counts" {default = 1}
variable "enable_execute_command" {default = true}
variable "alb_target_group_arn" {}
variable "subnet_ids" {}
variable "security_groups" {}
variable "assign_public_ip" {default = false}
variable "tags" {}
variable "container_name" {}

