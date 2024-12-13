from django.conf import settings
from django.core.mail import send_mail


def send_task_email(task):
    assignee = task.assignee
    subject = f"New Task Assigned: {task.title}"
    message = (
        f"You have been assigned a new task: {task.title}\n"
        f"Description: {task.description}\n"
        f"Priority: {task.get_priority_display()}\n"
        f"Due_Date: {task.due_date}"
    )
    send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,
        [assignee.email],
        fail_silently=False,
    )


def send_task_update_email(assignee_email, assignee_name, task_title):
    subject = "Task Updated"
    message = (
        f"Dear {assignee_name},\n\n"
        f"The task '{task_title}' has been updated by the creator.\n\n"
        "Please check the task details."
    )
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[assignee_email],
        fail_silently=False,
    )


def send_task_status_update_email(task):
    subject = "Task Status Updated"
    message = (
        f"Dear {task.creator.first_name},\n\n"
        f"The status of the task '{task.title}' has been updated by {task.assignee.first_name}.\n\n"
        "Please check the task status for more details."
    )
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[task.creator.email],
        fail_silently=False,
    )
