env = "dev"
region = "eu-west-1"
account_id = "038462750799"
stage_name = "v1"

vpc_cidr = "10.1.0.0/16"
public_cidrs = ["10.1.0.0/22", "10.1.4.0/22", "10.1.8.0/22"]
app_priv_cidrs = ["10.1.12.0/22", "10.1.16.0/22", "10.1.20.0/22"]
db_priv_cidrs = ["10.1.24.0/22", "10.1.28.0/22", "10.1.32.0/22"]

# vpc_cidr = "10.3.0.0/16"
# public_cidrs = ["10.3.0.0/22", "10.3.4.0/22", "10.3.8.0/22"]
# app_priv_cidrs = ["10.3.12.0/22", "10.3.16.0/22", "10.3.20.0/22"]
# db_priv_cidrs = ["10.3.24.0/22", "10.3.28.0/22", "10.3.32.0/22"]

# app_alb_arn = ""

# instance_type = "t3.xlarge"
# db_instance_class = "db.t2.2xlarge"
# max_allocated_storage = "100"
# min_allocated_storage = "20"

# database_engine = "mysql"
# database_engine_version = "8.0.30"

# backup_window = "03:53-04:23"
# rds_maintenance_window = "Sat:00:00-Sat:03:00"
# apply_immediately = "true"
