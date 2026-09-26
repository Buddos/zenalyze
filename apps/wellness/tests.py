from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import FinancialEntry


User = get_user_model()


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