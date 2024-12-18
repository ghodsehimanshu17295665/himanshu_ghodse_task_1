from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect, render
from django.views.generic import TemplateView, View

from .forms import CommentForm, LoginForms, SignupForms, SubTaskForm, TaskForm
from .models import Comment, SubTask, Task, User
from .utils import (
    send_task_email,
    send_task_status_update_email,
    send_task_update_email,
)


# Home page
class Home(TemplateView):
    """Home Page"""

    template_name = "index.html"


class SignupView(View):
    """Signup View - user Signup for task management system."""

    template_name = "signup.html"

    def get(self, request):
        form = SignupForms()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = SignupForms(request.POST)
        if form.is_valid():
            form.save()
            return redirect("login")
        return render(request, self.template_name, {"form": form})


class LoginView(TemplateView):
    """Login View - user login for task management system."""

    template_name = "login.html"

    def get(self, request):
        if request.user.is_authenticated:
            return redirect("task_list")
        form = LoginForms()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = LoginForms(data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                return redirect("task_list")

        return render(request, self.template_name, {"form": form})


class LogoutView(View):
    """Logout View - user logout for task management system."""

    def get(self, request):
        logout(request)
        return redirect("home_page")


class AssignTaskView(View):
    """AssignTaskView - User create a Task for another user."""

    def get(self, request):
        users = User.objects.exclude(id=request.user.id)
        form = TaskForm()
        return render(
            request, "assign_task.html", {"form": form, "users": users}
        )

    def post(self, request):
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.creator = request.user
            task.save()
            send_task_email(task)
            return redirect("create_subtask", task_id=task.id)
        else:
            return render(request, "assign_task.html", {"form": form})


class SubTaskView(View):
    """SubTaskView - User create a Task for another user."""

    def get(self, request, task_id):
        task = Task.objects.filter(id=task_id).first()
        subtask_form = SubTaskForm()
        return render(
            request,
            "sub_task.html",
            {"task": task, "subtask_form": subtask_form},
        )

    def post(self, request, task_id):
        task = Task.objects.filter(id=task_id).first()

        form = SubTaskForm(request.POST)
        if form.is_valid():
            subtask = form.save(commit=False)
            subtask.task = task
            subtask.save()

        subtasks = task.subtasks.all()
        subtask_form = SubTaskForm()

        return render(
            request,
            "sub_task.html",
            {"task": task, "subtask_form": subtask_form, "subtasks": subtasks},
        )


class TaskListView(View):
    """TaskListView - List of all Tasks."""

    template_name = "tasklist.html"

    def get(self, request):
        users = User.objects.all()
        task = Task.objects.all()

        assignee = request.GET.get("assignee")
        status = request.GET.get("status")
        due_date = request.GET.get("due_date")

        if assignee:
            task = task.filter(assignee__id=assignee)
        if status:
            task = task.filter(status=status)
        if due_date:
            task = task.filter(due_date=due_date)

        context = {
            "users": users,
            "task": task,
            "assignee": assignee,
            "status": status,
            "due_date": due_date,
        }
        return render(request, self.template_name, context)


class TaskDetailView(View):
    """TaskDetailView - Perticular Task related detail."""

    def get(self, request, pk):
        task = Task.objects.get(id=pk)
        comments = Comment.objects.filter(task=task)
        subtasks = task.subtasks.all()
        form = CommentForm()
        return render(
            request,
            "taskdetail.html",
            {
                "task": task,
                "subtasks": subtasks,
                "comments": comments,
                "form": form,
            },
        )

    def post(self, request, pk):
        task = Task.objects.get(id=pk)
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.task = task
            comment.save()
        comments = Comment.objects.filter(task=task)
        subtasks = task.subtasks.all()
        return render(
            request,
            "taskdetail.html",
            {
                "task": task,
                "subtasks": subtasks,
                "comments": comments,
                "form": form,
            },
        )


class TaskDeleteView(View):
    """TaskDeleteView - User Delete a task."""

    def post(self, request, pk):
        task = Task.objects.filter(id=pk).first()
        task.delete()
        return redirect("task_list")


class UserListView(View):
    """UserListView - List of all Users."""

    template_name = "userlist.html"

    def get(self, request):
        users = User.objects.all()
        context = {"users": users}
        return render(request, self.template_name, context=context)


class TaskUpdateView(View):
    """TaskUpdateView - User Update a task"""

    template_name = "taskupdate.html"

    def get(self, request, pk):
        user_id = request.user.id
        task = Task.objects.filter(id=pk, creator=user_id).first()
        if task:
            form = TaskForm(instance=task)
            return render(
                request, self.template_name, {"form": form, "task": task}
            )
        else:
            return redirect("task_list")

    def post(self, request, pk):
        task = Task.objects.filter(id=pk).first()
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            updated_task = form.save()
            if updated_task.assignee:
                send_task_update_email(
                    assignee_email=updated_task.assignee.email,
                    assignee_name=updated_task.assignee.username,
                    task_title=updated_task.title,
                )
            return redirect("task_list")
        return render(
            request, self.template_name, {"form": form, "task": task}
        )


class TaskStatusUpdateView(View):
    """TaskStatusUpdateView - User Update a task Status"""

    template_name = "task_status_update.html"

    def get(self, request, pk):
        # Fetch the main task and its associated sub-tasks
        task = Task.objects.filter(id=pk).first()
        sub_tasks = SubTask.objects.filter(task=task)

        if not request.user == task.assignee:
            return redirect("task_list")

        return render(
            request,
            self.template_name,
            {
                "task": task,
                "sub_tasks": sub_tasks,
            },
        )

    def post(self, request, pk):
        # Fetch the main task and its sub-tasks
        task = Task.objects.filter(id=pk).first()
        sub_tasks = SubTask.objects.filter(task=task)

        if sub_tasks.exists():
            # Update sub-task statuses from the form submission
            for sub_task in sub_tasks:
                new_status = request.POST.get(f"sub_task_status_{sub_task.id}")
                if new_status in ["Pending", "InProcessing", "Completed"]:
                    sub_task.status = new_status
                    sub_task.save()

            all_completed = True
            any_in_processing = False

            for sub_task in sub_tasks:
                if sub_task.status != "Completed":
                    all_completed = False
                if sub_task.status == "InProcessing":
                    any_in_processing = True

            if all_completed:
                task.status = "Completed"
            elif any_in_processing:
                task.status = "InProcessing"
            else:
                task.status = "Pending"

        else:
            # If no sub-tasks exist, allow direct updating of the main task's status
            new_task_status = request.POST.get("task_status")
            if new_task_status in ["Pending", "InProcessing", "Completed"]:
                task.status = new_task_status

        task.save()
        send_task_status_update_email(task)
        return redirect("task_list")
