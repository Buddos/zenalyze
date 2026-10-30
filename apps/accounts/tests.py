import re
import time
from io import BytesIO
from unittest.mock import Mock, patch

from django.contrib.auth import get_user_model
from django.contrib.sessions.models import Session
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from PIL import Image

from apps.accounts.models import UserSettings


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


class AccountRegistrationTests(TestCase):
    def test_auth_pages_use_google_identity_services_without_firebase(self):
        for route_name, auth_label, button_text in (
            ('accounts:login', 'Sign In', 'signin_with'),
            ('accounts:register', 'Create Free Account', 'signup_with'),
        ):
            with self.subTest(page=route_name):
                with override_settings(GOOGLE_CLIENT_ID='google-client-id'):
                    response = self.client.get(reverse(route_name))

                self.assertEqual(response.status_code, 200)
                self.assertContains(response, auth_label)
                self.assertNotContains(response, 'firebase')
                self.assertContains(response, 'https://accounts.google.com/gsi/client')
                self.assertContains(response, 'google-client-id')
                self.assertContains(response, button_text)

        self.assertEqual(reverse('accounts:google_auth'), '/auth/google/')
        self.assertEqual(self.client.get(reverse('accounts:google_auth')).status_code, 405)

    @override_settings(GOOGLE_CLIENT_ID='google-client-id')
    @patch('apps.accounts.views.http_requests.get')
    def test_google_id_token_creates_user_and_logs_in(self, token_request):
        token_response = Mock(status_code=200)
        token_response.json.return_value = {
            'aud': 'google-client-id',
            'iss': 'https://accounts.google.com',
            'exp': str(int(time.time()) + 3600),
            'sub': 'google-user-subject',
            'email': 'google-signup@example.test',
            'email_verified': 'true',
            'name': 'Google Signup',
            'picture': 'https://example.test/avatar.png',
        }
        token_request.return_value = token_response

        response = self.client.post(
            reverse('accounts:google_auth'),
            data='{"credential":"signed-google-id-token"}',
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'ok')
        self.assertTrue(response.json()['created'])
        user = User.objects.get(email='google-signup@example.test')
        self.assertEqual(user.full_name, 'Google Signup')
        self.assertFalse(user.has_usable_password())
        self.assertTrue(UserSettings.objects.filter(user=user).exists())
        self.assertEqual(str(user.pk), self.client.session['_auth_user_id'])
        self.assertEqual(token_request.call_args.kwargs['params'], {
            'id_token': 'signed-google-id-token',
        })

    @override_settings(GOOGLE_CLIENT_ID='google-client-id')
    @patch('apps.accounts.views.http_requests.get')
    def test_google_id_token_with_wrong_audience_is_rejected(self, token_request):
        token_response = Mock(status_code=200)
        token_response.json.return_value = {
            'aud': 'another-client-id',
            'iss': 'https://accounts.google.com',
            'exp': str(int(time.time()) + 3600),
            'sub': 'google-user-subject',
            'email': 'not-created@example.test',
            'email_verified': True,
        }
        token_request.return_value = token_response

        response = self.client.post(
            reverse('accounts:google_auth'),
            data='{"credential":"wrong-audience-token"}',
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 401)
        self.assertFalse(User.objects.filter(email='not-created@example.test').exists())

    @override_settings(GOOGLE_CLIENT_ID='google-client-id')
    def test_google_id_token_endpoint_requires_csrf_protection(self):
        client = Client(enforce_csrf_checks=True)
        response = client.post(
            reverse('accounts:google_auth'),
            data='{"credential":"signed-google-id-token"}',
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 403)

    def test_successful_registration_confirms_account_creation(self):
        response = self.client.post(reverse('accounts:register'), {
            'username': 'signup-confirmation-test',
            'email': 'signup-confirmation@example.test',
            'full_name': 'Signup Confirmation',
            'password': 'safe-test-pass-123',
            'confirm_password': 'safe-test-pass-123',
        }, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Account created successfully!')
        user = User.objects.get(username='signup-confirmation-test')
        self.assertEqual(user.email, 'signup-confirmation@example.test')
        self.assertTrue(user.check_password('safe-test-pass-123'))
        self.assertTrue(UserSettings.objects.filter(user=user).exists())
        self.assertEqual(str(user.pk), self.client.session['_auth_user_id'])


class ProfileAvatarUploadTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='avatar-user',
            email='avatar@example.test',
            password='safe-test-pass-123',
        )
        self.client.force_login(self.user)

    def make_png_upload(self):
        image_bytes = BytesIO()
        Image.new('RGB', (4, 4), color='teal').save(image_bytes, format='PNG')
        return SimpleUploadedFile('profile.png', image_bytes.getvalue(), content_type='image/png')

    def profile_payload(self, avatar):
        return {
            'full_name': 'Avatar Test User',
            'display_name': 'Avatar Test',
            'email': self.user.email,
            'emergency_contact_name': '',
            'emergency_contact_phone': '',
            'avatar': avatar,
        }

    def test_profile_page_renders_instant_avatar_preview_controls(self):
        response = self.client.get(reverse('accounts:profile'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id="profileAvatarInput"')
        self.assertContains(response, 'id="profileAvatarPreview"')
        self.assertContains(response, 'URL.createObjectURL(file)')

    @override_settings(IS_VERCEL=True, SUPABASE_URL='https://supabase.example.test')
    @patch.dict('os.environ', {'SUPABASE_SERVICE_ROLE_KEY': 'server-only-test-secret', 'SUPABASE_STORAGE_BUCKET': 'avatars'})
    @patch('apps.accounts.views.http_requests.post')
    def test_avatar_upload_saves_supabase_public_url(self, upload_request):
        upload_request.return_value = Mock()

        response = self.client.post(reverse('accounts:profile'), self.profile_payload(self.make_png_upload()))

        self.user.refresh_from_db()
        self.assertRedirects(response, reverse('accounts:profile'))
        self.assertEqual(
            self.user.avatar_url.split('/storage/v1/object/public/avatars/')[0],
            'https://supabase.example.test',
        )
        self.assertTrue(self.user.avatar_url.endswith('.png'))
        self.assertFalse(self.user.avatar)
        self.assertEqual(
            upload_request.call_args.args[0].split('/storage/v1/object/avatars/')[0],
            'https://supabase.example.test',
        )

    @override_settings(IS_VERCEL=True, SUPABASE_URL='https://supabase.example.test')
    @patch.dict('os.environ', {'SUPABASE_SERVICE_ROLE_KEY': 'server-only-test-secret'})
    @patch('apps.accounts.views.http_requests.post')
    def test_invalid_image_is_not_uploaded(self, upload_request):
        invalid_upload = SimpleUploadedFile('not-image.png', b'not an image', content_type='image/png')

        self.client.post(reverse('accounts:profile'), self.profile_payload(invalid_upload))

        upload_request.assert_not_called()
        self.user.refresh_from_db()
        self.assertFalse(self.user.avatar_url)

    @override_settings(IS_VERCEL=True, SUPABASE_URL='https://supabase.example.test')
    @patch.dict('os.environ', {}, clear=True)
    @patch('apps.accounts.views.http_requests.post')
    def test_missing_storage_credentials_do_not_write_local_avatar(self, upload_request):
        self.client.post(reverse('accounts:profile'), self.profile_payload(self.make_png_upload()))

        upload_request.assert_not_called()
        self.user.refresh_from_db()
        self.assertFalse(self.user.avatar_url)
        self.assertFalse(self.user.avatar)

    @override_settings(IS_VERCEL=True)
    def test_vercel_ignores_legacy_local_avatar_file(self):
        self.user.avatar = 'avatars/chat.jpeg'
        self.user.avatar_url = ''

        self.assertIsNone(self.user.avatar_display_url)

    @override_settings(IS_VERCEL=True)
    def test_vercel_prefers_persistent_supabase_avatar_url(self):
        self.user.avatar = 'avatars/chat.jpeg'
        self.user.avatar_url = 'https://supabase.example.test/storage/v1/object/public/avatars/user/photo.jpg'

        self.assertEqual(self.user.avatar_display_url, self.user.avatar_url)
