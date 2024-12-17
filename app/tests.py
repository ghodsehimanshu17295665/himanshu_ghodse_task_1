from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from app.models import Task


class HomeViewTest(TestCase):

    def test_home_get(self):
        response = self.client.get(reverse('home_page'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'index.html')


class SignupViewTest(TestCase):

    def test_signup_get(self):
        response = self.client.get(reverse('signup'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'signup.html')
        self.assertIn('form', response.context)

    def test_signup_post_valid(self):
        data = {
            'email': 'testuser@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'password1': 'securepassword123',
            'password2': 'securepassword123',
        }
        response = self.client.post(reverse('signup'), data)
        self.assertRedirects(response, reverse('login'))

        # Check if the user was created
        user = get_user_model().objects.get(email='testuser@example.com')
        self.assertEqual(user.email, 'testuser@example.com')


class LoginViewTest(TestCase):

    def setUp(self):
        self.User = get_user_model()
        self.user = self.User.objects.create_user(
            email='testuser@example.com',
            password='securepassword123',
            username='testuser'
        )
        self.login_url = reverse('login')

    def test_login_valid_user(self):
        data = {
            'username': 'testuser@example.com',
            'password': 'securepassword123',
        }
        response = self.client.post(self.login_url, data)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('task_list'))

        response = self.client.get(reverse('task_list'))
        self.assertEqual(response.context['user'].email, 'testuser@example.com')


class TaskListViewTest(TestCase):

    def setUp(self):
        self.User = get_user_model()
        self.user1 = self.User.objects.create_user(username='testuser1', email='user@gmail.com', password='password123')
        self.user2 = self.User.objects.create_user(username='testuser2', email='user2@gmail.com', password='password123')

        self.task1 = Task.objects.create(
            title='Task 1',
            description= 'Task 1 description',
            assignee=self.user1,
            creator=self.user2,
            status='Pending',
            priority='High',
            due_date=date(2025, 1, 1),
        )

        self.task2 = Task.objects.create(
            title='Task 2',
            description= 'Task 2 description',
            assignee=self.user2,
            creator=self.user1,
            status='Completed',
            priority='High',
            due_date=date(2025, 2, 1),
        )
        self.url = reverse('task_list')

    def test_get_request_all_tasks(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tasklist.html')
        self.assertEqual(len(response.context['task']), 2)

    def test_get_request_filter_assignee(self):
        response = self.client.get(self.url, {'assignee': self.user1.id})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tasklist.html')
        self.assertEqual(len(response.context['task']), 1)
        self.assertEqual(response.context['task'][0].assignee, self.user1)

    def test_get_request_filter_status(self):
        response = self.client.get(self.url, {'status': 'Completed'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tasklist.html')
        self.assertEqual(len(response.context['task']), 1)
        self.assertEqual(response.context['task'][0].status, 'Completed')

    def test_get_request_filter_due_date(self):
        response = self.client.get(self.url, {'due_date': '2025-01-01'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tasklist.html')
        self.assertEqual(len(response.context['task']), 1)
        self.assertEqual(response.context['task'][0].due_date, date(2025, 1, 1))


class AssignTaskViewTest(TestCase):

    def setUp(self):
        self.User = get_user_model()
        self.creator_user = self.User.objects.create_user(username='taskcreate', email='creator@gmail.com', password='password123')
        self.assign_user = self.User.objects.create_user(username='taskassign', email='assign@gmail.com', password='password123')
        self.url = reverse('assign_task')

    def test_get_assign_task_view(self):
        data = {
            'title': 'Task 1',
            'description': 'Task 1 description',
            'status': 'Pending',
            'priority': 'High',
            'assignee': self.assign_user.id,
            'due_date': '2025-01-01',
        }
        self.client.login(username='creator@gmail.com', password='password123')

        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("task_list"))

        task = Task.objects.get(title="Task 1")
        self.assertEqual(task.description, "Task 1 description")
        self.assertEqual(task.creator, self.creator_user)
        self.assertEqual(task.assignee, self.assign_user)

    def test_get_assign_task_invalid(self):
        data = {
            'title': 'Task 2',
            'description': 'Task 1 description',
            'status': 'Pending',
            'priority': ' ',
            'assignee': self.assign_user.id,
            'due_date': '',
        }
        self.client.login(username='creator@gmail.com', password='password123')
        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "assign_task.html")
        self.assertTrue(response.context["form"].errors)


class TaskUpdateViewTest(TestCase):

    def setUp(self):
        self.User = get_user_model()
        self.creator_user = self.User.objects.create_user(username='taskcreate', email='creator@gmail.com', password='password123')
        self.assign_user = self.User.objects.create_user(username='taskassign', email='assign@gmail.com', password='password123')
        self.task = Task.objects.create(
            title='Task 1',
            description= 'Task 1 description',
            assignee=self.assign_user,
            creator=self.creator_user,
            status='Pending',
            priority='High',
            due_date=date(2025, 1, 1),
        )
        self.url = reverse('update_task', kwargs={'pk': self.task.pk})

    def test_get_update_task(self):
        self.client.login(username='creator@gmail.com', password='password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'taskupdate.html')

    def test_post_task_update_success(self):
        data = {
            'title': 'Task 2',
            'description': 'Task 2 description',
            'status': 'InProcessing',
            'priority': 'Medium',
            'assignee': self.assign_user.id,
            'due_date': '2025-01-01',
        }
        self.client.login(username='creator@gmail.com', password='password123')
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)

        self.task.refresh_from_db()
        self.assertEqual(self.task.title, 'Task 2')
        self.assertEqual(self.task.description, 'Task 2 description')
        self.assertEqual(self.task.status, 'InProcessing')
        self.assertEqual(self.task.priority, 'Medium')
        self.assertRedirects(response, reverse('task_list'))


class TaskStatusUpdateViewTest(TestCase):

    def setUp(self):
        self.User = get_user_model()
        self.creator_user = self.User.objects.create_user(username='taskcreate', email='creator@gmail.com', password='password123')
        self.assign_user = self.User.objects.create_user(username='taskassign', email='assign@gmail.com', password='password123')
        self.task = Task.objects.create(
            title='Task 1',
            description= 'Task 1 description',
            assignee=self.assign_user,
            creator=self.creator_user,
            status='Pending',
            priority='High',
            due_date=date(2025, 1, 1),
        )
        self.url = reverse('status_update', kwargs={'pk': self.task.pk})

    def test_get_update_task(self):
        self.client.login(username='creator@gmail.com', password='password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'task_status_update.html')

    def test_post_task_status_update(self):
        data = {
            'status': 'Completed',
        }
        self.client.login(username='creator@gmail.com', password='password123')
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)

        self.task.refresh_from_db()
        self.assertEqual(self.task.status, 'Completed')
        self.assertRedirects(response, reverse('task_list'))
