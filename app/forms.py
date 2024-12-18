from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .models import Comment, SubTask, Task, User


class SignupForms(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)

    class Meta:
        model = User
        fields = ["email", "first_name", "last_name", "password1", "password2"]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.username = self.cleaned_data["email"]
        if commit:
            user.save()
        return user


class LoginForms(AuthenticationForm):
    username = forms.EmailField(label="Email", max_length=254, required=True)

    class Meta:
        fields = ["username", "password"]


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = [
            "title",
            "description",
            "status",
            "priority",
            "assignee",
            "due_date",
        ]


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["comment"]


class TaskStatusForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ["status"]


class SubTaskForm(forms.ModelForm):
    class Meta:
        model = SubTask
        fields = [
            "title",
            "description",
            "status",
        ]
