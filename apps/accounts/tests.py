import re
from io import BytesIO
from unittest.mock import Mock, patch

from django.contrib.auth import get_user_model
from django.contrib.sessions.models import Session
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from PIL import Image


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
        self.assertEqual(upload_request.call_args.args[0].split('/storage/v1/object/avatars/')[0], 'https://supabase.example.test')
        self.assertEqual(upload_request.call_args.kwargs['headers']['Authorization'], 'Bearer server-only-test-secret')

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