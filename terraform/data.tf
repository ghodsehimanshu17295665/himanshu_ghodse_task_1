data "aws_subnets" "app_subnets" {
  filter {
    name   = "vpc-id"
    values = [var.vpc_id]
  }

  # Only public subnets
  filter {
    name   = "map-public-ip-on-launch"
    values = ["true"]
  }
}
