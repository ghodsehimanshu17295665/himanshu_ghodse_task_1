from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Comment, Task, User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User
    list_display = (
        "id",
        "email",
        "first_name",
        "last_name",
    )
    search_fields = ("email", "first_name", "last_name")


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    model = Task
    list_display = (
        "id",
        "title",
        "creator",
        "assignee",
        "status",
        "priority",
        "due_date",
        "assigned_date",
    )


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    model = Comment
    list_display = ("id", "comment", "user", "task")
