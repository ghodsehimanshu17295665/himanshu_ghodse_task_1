from django.contrib.auth.models import AbstractUser
from django.db import models
from model_utils.models import TimeStampedModel


class User(AbstractUser, TimeStampedModel):
    id = models.AutoField(primary_key=True)
    email = models.EmailField(unique=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return self.email


class Task(TimeStampedModel):
    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Completed", "Completed"),
        ("InProcessing", "InProcessing"),
    ]
    PRIORITY_CHOICES = [
        ("Low", "Low"),
        ("Medium", "Medium"),
        ("High", "High"),
    ]
    creator = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="created_tasks"
    )
    assignee = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="assigned_tasks"
    )
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=100)
    description = models.TextField()
    status = models.CharField(
        max_length=50, choices=STATUS_CHOICES, default="Pending"
    )
    priority = models.CharField(max_length=50, choices=PRIORITY_CHOICES)
    assigned_date = models.DateField(auto_now_add=True)
    due_date = models.DateField()

    def __str__(self):
        return self.title


class Comment(TimeStampedModel):
    id = models.AutoField(primary_key=True)
    task = models.ForeignKey(
        Task, on_delete=models.CASCADE, related_name="comment"
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.CharField(max_length=100)

    def __str__(self):
        return f"comment by {self.user.email} on {self.task.title}"


class SubTask(TimeStampedModel):
    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("InProcessing", "InProcessing"),
        ("Completed", "Completed"),
    ]
    task = models.ForeignKey(
        Task, on_delete=models.CASCADE, related_name="subtasks"
    )
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=100)
    description = models.TextField()
    status = models.CharField(
        max_length=50, choices=STATUS_CHOICES, default="InProcessing"
    )

    def __str__(self):
        return self.title
