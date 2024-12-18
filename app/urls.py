from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from .views import (
    AssignTaskView,
    Home,
    LoginView,
    LogoutView,
    SignupView,
    SubTaskView,
    TaskDeleteView,
    TaskDetailView,
    TaskListView,
    TaskStatusUpdateView,
    TaskUpdateView,
    UserListView,
)

urlpatterns = [
    path("", Home.as_view(), name="home_page"),
    path("signup/page/", SignupView.as_view(), name="signup"),
    path("login/page/", LoginView.as_view(), name="login"),
    path("logout/page/", LogoutView.as_view(), name="logout"),
    path("task/list/", TaskListView.as_view(), name="task_list"),
    path("assign/task/", AssignTaskView.as_view(), name="assign_task"),
    path(
        "detail/task/<int:pk>/", TaskDetailView.as_view(), name="detail_task"
    ),
    path(
        "task/<int:pk>/comments/",
        TaskDetailView.as_view(),
        name="add_comments",
    ),
    path(
        "update/task/<int:pk>/", TaskUpdateView.as_view(), name="update_task"
    ),
    path(
        "delete/task/<int:pk>/", TaskDeleteView.as_view(), name="delete_task"
    ),
    path("user/list/", UserListView.as_view(), name="user_list"),
    path(
        "update/task/status/<int:pk>/",
        TaskStatusUpdateView.as_view(),
        name="status_update",
    ),
    path(
        "create-subtask/<int:task_id>/",
        SubTaskView.as_view(),
        name="create_subtask",
    ),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
