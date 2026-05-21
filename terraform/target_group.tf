resource "aws_lb_target_group" "app_tg" {
  name     = "django-tg"
  port     = 8000
  protocol = "HTTP"
  vpc_id   = var.vpc_id

  health_check {
    path                = "/"
    port                = "8000"
    healthy_threshold   = 2
    unhealthy_threshold = 2
    timeout             = 5
    interval            = 10
    matcher             = "200"
  }

  tags = {
    Name = "django-tg"
  }
}
