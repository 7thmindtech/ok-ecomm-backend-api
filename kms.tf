
resource "aws_kms_key" "ok_cluster_key" {
  description             = "ecs cluster kms key"
  deletion_window_in_days = 7
}