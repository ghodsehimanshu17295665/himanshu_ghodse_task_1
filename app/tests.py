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
        self.assertRedirects(response, reverse('tasklist'))

        response = self.client.get(reverse('tasklist'))
        self.assertEqual(response.context['user'].email, 'testuser@example.com')


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

    def test_get_request_filter_by_assignee(self):
        response = self.client.get(self.url, {'assignee': self.user1.id})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tasklist.html')
        self.assertEqual(len(response.context['task']), 1)

    def test_get_request_filter_by_status(self):
        response = self.client.get(self.url, {'status': 'Completed'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tasklist.html')
        self.assertEqual(len(response.context['task']), 1)

    def test_get_request_filter_by_due_date(self):
        response = self.client.get(self.url, {'due_date': '2025-01-01'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tasklist.html')
        self.assertEqual(len(response.context['task']), 1)
