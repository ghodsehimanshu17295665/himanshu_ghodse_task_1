#  1. Provider (ALWAYS TOP)
provider "aws" {
  region = "us-east-1"
}

#  2. Security Group
resource "aws_security_group" "alb_sg" {
  name   = "alb-sg"
  vpc_id = "vpc-09d6552853b421e99"

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

#  3. ALB
resource "aws_lb" "app_alb" {
  name               = "django-alb"
  load_balancer_type = "application"

  subnets = [
    "subnet-054a76f3a410ca963",
    "subnet-073211ff018bd16b4"
  ]

  security_groups = [aws_security_group.alb_sg.id]
}

#  4. Target Group
resource "aws_lb_target_group" "app_tg" {
  name     = "django-tg"
  port     = 8000
  protocol = "HTTP"
  vpc_id   = "vpc-09d6552853b421e99"

  health_check {
    path = "/"
    port = "8000"
  }
}

#  5. Attach EC2
resource "aws_lb_target_group_attachment" "app_attach" {
  target_group_arn = aws_lb_target_group.app_tg.arn
  target_id        = "i-0be276c052b44a18b"
  port             = 8000
}

# 6. Listener
resource "aws_lb_listener" "app_listener" {
  load_balancer_arn = aws_lb.app_alb.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.app_tg.arn
  }
}