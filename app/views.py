from django.shortcuts import render, redirect
from django.views.generic import TemplateView, View
from .forms import SignupForms, LoginForms, TaskForm, CommentForm, TaskStatusForm
from django.contrib.auth import login, logout, authenticate
from .models import User, Task, Comment
from django.core.mail import send_mail
from django.conf import settings


# Home page
class Home(TemplateView):
    template_name = "index.html"


class SignupView(View):
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
    template_name = "login.html"

    def get(self, request):
        if request.user.is_authenticated:
            return redirect("tasklist")
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
                return redirect("tasklist")
        return render(request, self.template_name, {"form": form})


class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect("home_page")


class AssignTaskView(View):
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

            # Send email
            assignee = task.assignee
            subject = f"New Task Assigned: {task.title}"
            message = f"You have been assigned a new task: {task.title}\nDescription: {task.description}\nPriority: {task.get_priority_display()}\nDue_Date: {task.due_date}"
            send_mail(
                subject,
                message,
                settings.EMAIL_HOST_USER,
                [assignee.email],
                fail_silently=False,
            )
            return redirect("tasklist")
        else:
            return render(request, "assign_task.html", {"form": form})


class TaskListView(View):
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
    def get(self, request, pk):
        task = Task.objects.get(id=pk)
        comments = Comment.objects.filter(task=task)
        form = CommentForm()
        return render(
            request,
            "taskdetail.html",
            {"task": task, "comments": comments, "form": form},
        )

    def post(self, request, pk):
        task = Task.objects.get(id=pk)
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.task = task
            comment.save()
            return redirect("tasklist")
        comments = Comment.objects.filter(task=task)
        return render(
            request,
            "taskdetail.html",
            {"task": task, "comments": comments, "form": form},
        )

class TaskDeleteView(View):
    def post(self, request, pk):
        task = Task.objects.filter(id=pk).first()
        task.delete()
        return redirect("tasklist")


class UserListView(View):
    template_name = "userlist.html"

    def get(self, request):
        user = User.objects.all()
        context = {"user": user}
        return render(request, self.template_name, context=context)


class TaskUpdateView(View):
    template_name = "taskupdate.html"

    def get(self, request, pk):
        task = Task.objects.filter(id=pk).first()
        form = TaskForm(instance=task)
        return render(request, self.template_name, {'form': form, 'task': task})

    def post(self, request, pk):
        task = Task.objects.filter(id=pk).first()
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            updated_task = form.save()
            return redirect('tasklist')
        return render(request, self.template_name, {'form': form, 'task': task})


class TaskStatusUpdateView(View):
    template_name = "task_status_update.html"

    def get(self, request, pk):
        task = Task.objects.filter(id=pk).first()
        form = TaskStatusForm(instance=task)
        return render(request, self.template_name, {'form': form, 'task': task})
    
    def post(self, request, pk):
        task = Task.objects.filter(id=pk).first()
        form = TaskStatusForm(request.POST, instance=task)
        if form.is_valid():
            update_status = form.save()
            return redirect('tasklist')
        return render(request, self.template_name, {'form': form, 'task': task})
