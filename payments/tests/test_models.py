from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase

from payments.models import Payment
from payments.tests.helpers import sample_borrowing, sample_payment


class PaymentModelTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="user@test.com",
            password="testpassword123",
        )

        self.borrowing = sample_borrowing(user=self.user)

    def test_payment_creation_successful(self):
        payment = sample_payment(borrowing=self.borrowing)

        self.assertIsNotNone(payment.id)
        self.assertEqual(payment.status, Payment.Status.PENDING)
        self.assertEqual(payment.type, Payment.Type.PAYMENT)
        self.assertEqual(payment.borrowing, self.borrowing)
        self.assertEqual(payment.money_to_pay, Decimal("10.50"))

    def test_payment_str(self):
        payment = sample_payment(borrowing=self.borrowing)

        self.assertEqual(str(payment), "PAYMENT - PENDING (10.50 USD)")
