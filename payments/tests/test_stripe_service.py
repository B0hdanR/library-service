from decimal import Decimal
from unittest.mock import patch, MagicMock

from django.contrib.auth import get_user_model
from django.test import TestCase

from payments.models import Payment
from payments.stripe_service import (
    calculate_borrowing_total_price,
    create_stripe_session,
)
from payments.tests.helpers import sample_borrowing


class StripeServiceTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="user@test.com",
            password="testpassword123",
        )
        self.borrowing = sample_borrowing(user=self.user)

    def test_calculate_borrowing_total_price(self):
        total_price = calculate_borrowing_total_price(self.borrowing)

        self.assertEqual(total_price, Decimal("10.50"))

    @patch("payments.stripe_service.stripe.checkout.Session.create")
    def test_create_stripe_session_creates_payment(self, mock_session_create):
        mock_session_create.return_value = MagicMock(
            url="https://checkout.stripe.com/c/pay/cs_test_fake",
            id="cs_test_fake",
        )

        payment = create_stripe_session(self.borrowing)

        self.assertEqual(Payment.objects.count(), 1)
        self.assertEqual(payment.borrowing, self.borrowing)
        self.assertEqual(payment.status, Payment.Status.PENDING)
        self.assertEqual(payment.type, Payment.Type.PAYMENT)
        self.assertEqual(payment.money_to_pay, Decimal("10.50"))
        self.assertEqual(payment.session_url, "https://checkout.stripe.com/c/pay/cs_test_fake")
        self.assertEqual(payment.session_id, "cs_test_fake")

    @patch("payments.stripe_service.stripe.checkout.Session.create")
    def test_create_stripe_session_converts_price_to_cents(self, mock_session_create):
        mock_session_create.return_value = MagicMock(
            url="https://checkout.stripe.com/c/pay/cs_test_fake",
            id="cs_test_fake",
        )

        create_stripe_session(self.borrowing)

        call_kwargs = mock_session_create.call_args.kwargs
        unit_amount = call_kwargs["line_items"][0]["price_data"]["unit_amount"]

        self.assertEqual(unit_amount, 1050)
        self.assertEqual(call_kwargs["line_items"][0]["quantity"], 1)
        self.assertEqual(call_kwargs["mode"], "payment")
