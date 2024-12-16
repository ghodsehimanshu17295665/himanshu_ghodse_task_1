from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from app.models import Task, Comment
from datetime import date
from .forms import CommentForm


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
        self.assertRedirects(response, reverse('tasklist'))

        response = self.client.get(reverse('tasklist'))
        self.assertEqual(response.context['user'].email, 'testuser@example.com')

    def test_login_invalid_user(self):
        data = {
            'username': 'testuser@example.com',
            'password': 'wrongpassword',
        }
        response = self.client.post(self.login_url, data)

        self.assertEqual(response.status_code, 200)

        form = response.context['form']

        non_field_errors = form.non_field_errors()

        self.assertTrue(any('Please enter a correct email and password' in error for error in non_field_errors))


class LogoutViewTest(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='password123'
        )
        self.logout_url = reverse('logout')
        self.home_url = reverse('home_page')

    def test_logout_redirect(self):
        self.client.login(username='testuser', password='password123')
        response = self.client.get(self.logout_url)
        self.assertRedirects(response, self.home_url)

    def test_logged_out_user_redirect(self):
        self.client.logout()
        response = self.client.get(self.logout_url)
        self.assertRedirects(response, self.home_url)


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
        self.url = reverse('tasklist')

    def test_get_request_all_tasks(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tasklist.html')
        self.assertEqual(len(response.context['task']), 2)
        self.assertEqual(len(response.context['users']), 2)

    def test_get_request_filter_by_assignee(self):
        response = self.client.get(self.url, {'assignee': self.user1.id})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tasklist.html')
        self.assertEqual(len(response.context['task']), 1)
        self.assertEqual(response.context['task'][0].assignee, self.user1)

    def test_get_request_filter_by_status(self):
        response = self.client.get(self.url, {'status': 'Completed'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tasklist.html')
        self.assertEqual(len(response.context['task']), 1)
        self.assertEqual(response.context['task'][0].status, 'Completed')


class TaskDetailViewTest(TestCase):
    def setUp(self):
        self.User = get_user_model()
        self.user1 = self.User.objects.create_user(username='testuser1', email='user@gmail.com', password='password123')
        self.user2 = self.User.objects.create_user(username='testuser2', email='user2@gmail.com', password='password123')

        self.task = Task.objects.create(
            title="Task 1",
            description="This is a test task1 description",
            assignee=self.user1,
            creator=self.user2,
            status="Pending",
            priority="Low",
            due_date=date(2025, 1, 1),
        )
        self.comment1 = Comment.objects.create(
            user=self.user2,
            task=self.task,
            comment="This is the first comment."
        )
        self.url = reverse('detailtask', kwargs={'pk': self.task.id})
        self.client.logout()


    def test_get_request(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'taskdetail.html')

        self.assertEqual(response.context['task'], self.task)
        self.assertIn(self.comment1, response.context['comments'])

        self.assertTrue(isinstance(response.context['form'], CommentForm))

    def test_post_request_valid_comment(self):
        data = {'comment': 'This is a new comment.'}

        # Attempt login and check result
        login_success = self.client.login(username='user@gmail.com', password='password123')
        self.assertTrue(login_success, "Login failed!")

        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Comment.objects.count(), 2)
        self.assertEqual(Comment.objects.last().comment, 'This is a new comment.')
        self.assertIn(Comment.objects.last(), response.context['comments'])
        self.assertTrue(isinstance(response.context['form'], CommentForm))
