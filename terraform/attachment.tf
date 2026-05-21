resource "aws_lb_target_group_attachment" "app_attach" {
  target_group_arn = aws_lb_target_group.app_tg.arn

  target_id = var.instance_id

  port = 8000
}