from decimal import Decimal
from datetime import datetime, timedelta

from django.contrib.auth import get_user_model
from django.contrib.staticfiles import finders
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Exercise, FinancialEntry
from apps.community.models import MediaAsset
from apps.core.management.commands.seed_zenalyze import Command as SeedZenalyzeCommand


User = get_user_model()


class PracticeMediaRenderingTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='practice-media-user',
            email='practice-media@example.test',
            password='safe-test-pass-123',
        )
        self.client.force_login(self.user)

    def test_video_practice_renders_playback_controls_and_thumbnail(self):
        asset = MediaAsset.objects.create(
            asset_type='video',
            file='uploads/exercises/videos/meditation.mp4',
            thumbnail='uploads/exercises/thumbnails/meditation.jpg',
            processing_status='ready',
        )
        Exercise.objects.create(
            title='Guided meditation video',
            category='meditation',
            media_asset=asset,
            status='published',
        )

        response = self.client.get(reverse('wellness:exercises'))

        self.assertContains(response, 'controls preload="metadata" playsinline')
        self.assertContains(response, '/media/uploads/exercises/videos/meditation.mp4')
        self.assertContains(response, '/media/uploads/exercises/thumbnails/meditation.jpg')

    def test_seeded_breathing_media_is_available_from_staticfiles(self):
        Exercise.objects.create(
            title='Static guided breathing',
            category='breathing',
            video_type='file',
            video_url='/static/uploads/exercises/videos/exercise_6a09f6bd75a97.mp4',
            thumbnail_image='/static/uploads/exercises/thumbnails/thumb_6a0a01df4eefb.jpeg',
            status='published',
        )

        response = self.client.get(reverse('wellness:exercises'))

        self.assertTrue(finders.find('uploads/exercises/videos/exercise_6a09f6bd75a97.mp4'))
        self.assertContains(response, '/static/uploads/exercises/videos/exercise_6a09f6bd75a97.mp4')
        self.assertContains(response, '/static/uploads/exercises/thumbnails/thumb_6a0a01df4eefb.jpeg')

    def test_practice_without_a_thumbnail_uses_local_category_artwork(self):
        Exercise.objects.create(
            title='Quiet meditation',
            category='meditation',
            is_guided=True,
            status='published',
        )

        response = self.client.get(reverse('wellness:exercises'))

        self.assertContains(response, '/static/images/practices/meditation.svg')
        self.assertContains(response, 'data-fallback="/static/images/practices/meditation.svg"')

    def test_seed_cleanup_detaches_breathing_media_from_meditation(self):
        asset = MediaAsset.objects.create(
            asset_type='video',
            file='uploads/exercises/videos/breathing.mp4',
            thumbnail='uploads/exercises/thumbnails/breathing.webp',
            processing_status='ready',
        )
        exercise = Exercise.objects.create(
            title='Mindfulness Body Scan Meditation',
            category='meditation',
            video_file='uploads/exercises/videos/breathing.mp4',
            thumbnail_file='uploads/exercises/thumbnails/breathing.webp',
            media_asset=asset,
        )

        SeedZenalyzeCommand().detach_legacy_breathing_media(
            exercise.title,
            'uploads/exercises/videos/breathing.mp4',
            'uploads/exercises/thumbnails/breathing.webp',
        )

        exercise.refresh_from_db()
        self.assertFalse(exercise.video_file)
        self.assertFalse(exercise.thumbnail_file)
        self.assertIsNone(exercise.media_asset_id)


class FinancialPlannerTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='planner-user',
            email='planner@example.test',
            password='safe-test-pass-123',
        )
        self.client.force_login(self.user)

    def test_currency_filter_does_not_create_a_transaction(self):
        FinancialEntry.objects.create(
            user=self.user,
            amount=Decimal('2400.00'),
            category='Income',
            currency='KES',
        )

        response = self.client.get(reverse('wellness:financial'), {'currency': 'USD'})

        self.assertEqual(FinancialEntry.objects.count(), 1)
        self.assertEqual(response.context['display_currency'], 'USD')
        self.assertEqual(response.context['total_income'], Decimal('0'))

    def test_valid_entry_is_saved_and_redirect_keeps_currency(self):
        response = self.client.post(reverse('wellness:financial'), {
            'action': 'create_entry',
            'amount': '85.50',
            'category': 'Food',
            'currency': 'USD',
            'description': 'Weekly groceries',
        })

        entry = FinancialEntry.objects.get()
        self.assertEqual(entry.amount, Decimal('85.50'))
        self.assertEqual(entry.currency, 'USD')
        self.assertRedirects(response, f"{reverse('wellness:financial')}?currency=USD")

    def test_invalid_amount_is_not_saved(self):
        self.client.post(reverse('wellness:financial'), {
            'action': 'create_entry',
            'amount': '-4',
            'category': 'Food',
            'currency': 'KES',
        })

        self.assertFalse(FinancialEntry.objects.exists())

    def test_non_finite_and_over_precision_amounts_are_rejected(self):
        for amount in ('NaN', 'Infinity', '12.345'):
            with self.subTest(amount=amount):
                self.client.post(reverse('wellness:financial'), {
                    'action': 'create_entry',
                    'amount': amount,
                    'category': 'Food',
                    'currency': 'KES',
                })

        self.assertFalse(FinancialEntry.objects.exists())

    def test_planner_renders_currency_insights_and_empty_state(self):
        response = self.client.get(reverse('wellness:financial'))

        self.assertContains(response, 'Your financial picture')
        self.assertContains(response, 'Where it goes')
        self.assertContains(response, 'Your KES ledger is ready')

    def test_totals_are_scoped_to_selected_currency(self):
        FinancialEntry.objects.create(
            user=self.user,
            amount=Decimal('1000.00'),
            category='Income',
            currency='KES',
        )
        FinancialEntry.objects.create(
            user=self.user,
            amount=Decimal('10.00'),
            category='Food',
            currency='USD',
        )

        response = self.client.get(reverse('wellness:financial'), {'currency': 'USD'})

        self.assertEqual(response.context['total_income'], Decimal('0'))
        self.assertEqual(response.context['total_expense'], Decimal('10.00'))
        self.assertEqual(response.context['net_balance'], Decimal('-10.00'))

    def test_savings_are_separate_from_expenses_in_planner_totals(self):
        FinancialEntry.objects.create(
            user=self.user,
            amount=Decimal('100.00'),
            category='Income',
            currency='KES',
        )
        FinancialEntry.objects.create(
            user=self.user,
            amount=Decimal('30.00'),
            category='Food',
            currency='KES',
        )
        FinancialEntry.objects.create(
            user=self.user,
            amount=Decimal('20.00'),
            category='Savings',
            currency='KES',
        )

        response = self.client.get(reverse('wellness:financial'))

        self.assertEqual(response.context['total_expense'], Decimal('30.00'))
        self.assertEqual(response.context['total_savings'], Decimal('20.00'))
        self.assertEqual(response.context['net_balance'], Decimal('50.00'))

    def test_financial_insights_analyze_user_transactions_and_savings(self):
        today = timezone.localdate()
        previous_month = today.replace(day=1) - timedelta(days=1)
        FinancialEntry.objects.create(
            user=self.user,
            amount=Decimal('1000.00'),
            category='Income',
            currency='KES',
        )
        FinancialEntry.objects.create(
            user=self.user,
            amount=Decimal('350.00'),
            category='Housing',
            currency='KES',
        )
        FinancialEntry.objects.create(
            user=self.user,
            amount=Decimal('150.00'),
            category='Savings',
            currency='KES',
        )
        old_expense = FinancialEntry.objects.create(
            user=self.user,
            amount=Decimal('200.00'),
            category='Food',
            currency='KES',
        )
        old_expense.created_at = timezone.make_aware(
            datetime(previous_month.year, previous_month.month, 15, 12, 0)
        )
        old_expense.save(update_fields=['created_at'])

        response = self.client.get(reverse('wellness:financial_insights'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['month_income'], Decimal('1000.00'))
        self.assertEqual(response.context['month_expenses'], Decimal('350.00'))
        self.assertEqual(response.context['month_savings'], Decimal('150.00'))
        self.assertEqual(response.context['remaining'], Decimal('500.00'))
        self.assertEqual(response.context['previous_expenses'], Decimal('200.00'))
        self.assertContains(response, 'Financial Insights')
        self.assertContains(response, 'Six-month cash flow')

    def test_delete_button_removes_owned_transaction_and_keeps_currency(self):
        entry = FinancialEntry.objects.create(
            user=self.user,
            amount=Decimal('12.00'),
            category='Food',
            currency='USD',
        )
        page = self.client.get(reverse('wellness:financial'), {'currency': 'USD'})
        self.assertContains(page, reverse('wellness:financial_delete', args=[entry.id]))

        response = self.client.post(reverse('wellness:financial_delete', args=[entry.id]), {'currency': 'USD'})

        self.assertRedirects(response, f"{reverse('wellness:financial')}?currency=USD")
        self.assertFalse(FinancialEntry.objects.filter(id=entry.id).exists())

    def test_stale_or_other_users_transaction_id_does_not_show_404(self):
        other_user = User.objects.create_user(
            username='another-planner-user',
            email='another-planner@example.test',
            password='safe-test-pass-123',
        )
        other_entry = FinancialEntry.objects.create(
            user=other_user,
            amount=Decimal('12.00'),
            category='Food',
            currency='KES',
        )

        response = self.client.post(reverse('wellness:financial_delete', args=[other_entry.id]), {'currency': 'KES'})

        self.assertRedirects(response, f"{reverse('wellness:financial')}?currency=KES")
        self.assertTrue(any(
            'That transaction was not found in your account.' in str(message)
            for message in response.wsgi_request._messages
        ))
        self.assertTrue(FinancialEntry.objects.filter(id=other_entry.id).exists())