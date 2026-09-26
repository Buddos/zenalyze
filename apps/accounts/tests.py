import re

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse


User = get_user_model()


class LoginCSRFTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='csrf-login-user',
            email='csrf-login@example.test',
            password='safe-test-pass-123',
        )
        self.client = Client(enforce_csrf_checks=True)

    def test_login_form_posts_its_csrf_token_and_is_not_cacheable(self):
        response = self.client.get(reverse('accounts:login'))

        self.assertEqual(response.status_code, 200)
        self.assertIn('no-store', response['Cache-Control'])
        self.assertIn('csrftoken', self.client.cookies)
        token_match = re.search(rb'name="csrfmiddlewaretoken" value="([^"]+)"', response.content)
        self.assertIsNotNone(token_match)

        post_response = self.client.post(reverse('accounts:login'), {
            'username': self.user.username,
            'password': 'safe-test-pass-123',
            'csrfmiddlewaretoken': token_match.group(1).decode(),
        })

        self.assertEqual(post_response.status_code, 302)
        self.assertEqual(post_response.url, reverse('wellness:dashboard'))

    def test_login_rejects_missing_csrf_token(self):
        response = self.client.post(reverse('accounts:login'), {
            'username': self.user.username,
            'password': 'safe-test-pass-123',
        })

        self.assertEqual(response.status_code, 403)