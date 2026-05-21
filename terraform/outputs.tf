output "alb_dns" {
  value = aws_lb.app_alb.dns_name
}

output "subnets_used" {
  value = data.aws_subnets.app_subnets.ids
}
