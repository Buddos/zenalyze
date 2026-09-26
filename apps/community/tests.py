import json
import tempfile

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

from apps.administration.models import ContentModeration
from apps.wellness.models import Exercise, UserExerciseSession

from .models import CommunityPost, MediaAsset, PostMedia


User = get_user_model()


class MediaPostTests(TestCase):
    def setUp(self):
        self.media_dir = tempfile.TemporaryDirectory()
        self.settings_override = override_settings(MEDIA_ROOT=self.media_dir.name)
        self.settings_override.enable()
        self.user = User.objects.create_user(
            username='community-member',
            email='community@example.test',
            password='safe-test-pass-123',
        )
        self.client.force_login(self.user)

    def tearDown(self):
        self.settings_override.disable()
        self.media_dir.cleanup()

    def image_upload(self, name='image.jpg'):
        return SimpleUploadedFile(name, b'image-content', content_type='image/jpeg')

    def test_media_post_is_pending_until_moderator_approves(self):
        response = self.client.post(reverse('community:create_post'), {
            'content': 'A visual reflection',
            'media_files': [self.image_upload()],
        })

        post = CommunityPost.objects.get()
        asset = MediaAsset.objects.get()
        moderation = ContentModeration.objects.get(content_id=post.id)
        self.assertRedirects(response, reverse('community:community'))
        self.assertEqual(post.moderation_status, 'pending')
        self.assertEqual(asset.asset_type, 'image')
        self.assertEqual(PostMedia.objects.get(post=post).position, 0)
        self.assertEqual(moderation.status, 'pending')

        feed_response = self.client.get(reverse('community:community'))
        self.assertFalse(feed_response.context['posts'].filter(pk=post.pk).exists())

        moderator = User.objects.create_superuser(
            username='moderator',
            email='moderator@example.test',
            password='safe-test-pass-123',
        )
        self.client.force_login(moderator)
        self.client.post(reverse('administration:review_moderation', args=[moderation.id, 'approve']))
        post.refresh_from_db()
        self.assertEqual(post.moderation_status, 'visible')

    def test_text_only_post_is_visible_without_moderation(self):
        self.client.post(reverse('community:create_post'), {
            'title': 'A small win',
            'content': 'I took a mindful break today.',
        })

        post = CommunityPost.objects.get()
        self.assertEqual(post.moderation_status, 'visible')
        self.assertFalse(ContentModeration.objects.exists())

    def test_more_than_six_images_are_rejected(self):
        self.client.post(reverse('community:create_post'), {
            'content': 'Too many images',
            'media_files': [self.image_upload(f'image-{index}.jpg') for index in range(7)],
        })

        self.assertFalse(CommunityPost.objects.exists())
        self.assertFalse(MediaAsset.objects.exists())


class PublishedPracticeTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='practice-member',
            email='practice@example.test',
            password='safe-test-pass-123',
        )
        self.client.force_login(self.user)

    def test_practice_page_only_shows_published_matching_category(self):
        breathing = Exercise.objects.create(
            title='Breathing practice',
            category='breathing',
            is_guided=True,
            instructions='Breathe slowly.',
            status='published',
        )
        Exercise.objects.create(
            title='Draft practice',
            category='breathing',
            status='draft',
        )
        Exercise.objects.create(
            title='Published yoga',
            category='yoga_flow',
            status='published',
        )

        response = self.client.get(reverse('wellness:exercises'), {'cat': 'breathing'})

        self.assertEqual(list(response.context['exercises']), [breathing])
        self.assertContains(response, 'Breathing practice')
        self.assertNotContains(response, 'Draft practice')
        self.assertNotContains(response, 'Published yoga')

    def test_session_completes_at_ninety_percent(self):
        exercise = Exercise.objects.create(
            title='One minute practice',
            category='breathing',
            duration_minutes=1,
            is_guided=True,
            status='published',
        )
        start_response = self.client.post(reverse('wellness:start_exercise_session', args=[exercise.id]))
        session_id = start_response.json()['session_id']

        before_threshold = self.client.post(
            reverse('wellness:update_exercise_session', args=[session_id]),
            data=json.dumps({'progress_seconds': 53}),
            content_type='application/json',
        )
        self.assertFalse(before_threshold.json()['completed'])
        practice_page = self.client.get(reverse('wellness:exercises'))
        dashboard_page = self.client.get(reverse('wellness:dashboard'))
        self.assertEqual(practice_page.context['continue_session'].id, session_id)
        self.assertEqual(dashboard_page.context['continue_session'].id, session_id)

        at_threshold = self.client.post(
            reverse('wellness:update_exercise_session', args=[session_id]),
            data=json.dumps({'progress_seconds': 54}),
            content_type='application/json',
        )
        self.assertTrue(at_threshold.json()['completed'])
        self.assertTrue(UserExerciseSession.objects.get(id=session_id).completed)