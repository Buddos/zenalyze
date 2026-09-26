import re

from django.contrib.auth import get_user_model
from django.contrib.sessions.models import Session
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
        response = self.client.get(reverse('accounts:login'), secure=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn('no-store', response['Cache-Control'])
        self.assertIn('csrftoken', self.client.cookies)
        token_match = re.search(rb'name="csrfmiddlewaretoken" value="([^"]+)"', response.content)
        self.assertIsNotNone(token_match)

        post_response = self.client.post(reverse('accounts:login'), {
            'username': self.user.username,
            'password': 'safe-test-pass-123',
            'csrfmiddlewaretoken': token_match.group(1).decode(),
        }, secure=True, HTTP_ORIGIN='https://zenalyze-six.vercel.app')

        self.assertEqual(post_response.status_code, 302)
        self.assertEqual(post_response.url, reverse('wellness:dashboard'))
        session_key = self.client.session.session_key
        stored_session = Session.objects.get(session_key=session_key)
        self.assertEqual(stored_session.get_decoded()['_auth_user_id'], str(self.user.id))

    def test_stale_login_token_returns_a_fresh_form(self):
        response = self.client.get(reverse('accounts:login'), secure=True)
        old_cookie = self.client.cookies['csrftoken'].value

        response = self.client.post(reverse('accounts:login'), {
            'username': 'nonexistent-csrf-diagnostic-user',
            'password': 'not-a-real-password',
            'csrfmiddlewaretoken': 'invalid-stale-token',
        }, secure=True, HTTP_ORIGIN='https://zenalyze-six.vercel.app')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Your security token expired. Please try again.')
        self.assertNotEqual(self.client.cookies['csrftoken'].value, old_cookie)
        self.assertIn(b'name="csrfmiddlewaretoken"', response.content)

    def test_registration_form_is_uncached_and_recovers_from_stale_token(self):
        response = self.client.get(reverse('accounts:register'), secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('no-store', response['Cache-Control'])
        old_cookie = self.client.cookies['csrftoken'].value

        response = self.client.post(reverse('accounts:register'), {
            'username': 'csrf-register-test',
            'email': 'csrf-register@example.test',
            'password': 'safe-test-pass-123',
            'confirm_password': 'safe-test-pass-123',
            'csrfmiddlewaretoken': 'invalid-stale-token',
        }, secure=True, HTTP_ORIGIN='https://zenalyze-six.vercel.app')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Your security token expired. Please try again.')
        self.assertNotEqual(self.client.cookies['csrftoken'].value, old_cookie)
        self.assertFalse(User.objects.filter(username='csrf-register-test').exists())