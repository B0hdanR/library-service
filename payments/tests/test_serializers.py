from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase

from payments.models import Payment
from payments.serializers import PaymentListSerializer, PaymentDetailSerializer
from payments.tests.helpers import sample_borrowing, sample_payment


class PaymentSerializerTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="user@test.com",
            password="testpassword123",
        )

        self.borrowing = sample_borrowing(user=self.user)

    def test_list_serializer_contains_expected_fields(self):
        payment = sample_payment(borrowing=self.borrowing)

        serializer = PaymentListSerializer(payment)

        self.assertEqual(serializer.data["id"], payment.id)
        self.assertEqual(serializer.data["status"], Payment.Status.PENDING)
        self.assertEqual(serializer.data["type"], Payment.Type.PAYMENT)
        self.assertEqual(serializer.data["borrowing_id"], self.borrowing.id)
        self.assertEqual(serializer.data["money_to_pay"], "10.50")
        self.assertNotIn("session_url", serializer.data)
        self.assertNotIn("session_id", serializer.data)

    def test_detail_serializer_contains_all_fields(self):
        payment = sample_payment(
            borrowing=self.borrowing,
            session_url="https://example.com/session",
            session_id="session_test",
        )

        serializer = PaymentDetailSerializer(payment)

        self.assertEqual(serializer.data["id"], payment.id)
        self.assertEqual(serializer.data["status"], Payment.Status.PENDING)
        self.assertEqual(serializer.data["type"], Payment.Type.PAYMENT)
        self.assertEqual(serializer.data["borrowing"], self.borrowing.id)
        self.assertEqual(serializer.data["session_url"], "https://example.com/session")
        self.assertEqual(serializer.data["session_id"], "session_test")
        self.assertEqual(serializer.data["money_to_pay"], "10.50")

    def test_list_serializer_fields_are_read_only(self):
        serializer = PaymentListSerializer()

        for field in ("id", "status", "type", "borrowing_id", "money_to_pay"):
            self.assertTrue(serializer.fields[field].read_only)

    def test_detail_serializer_fields_are_read_only(self):
        serializer = PaymentDetailSerializer()

        for field in (
            "id",
            "status",
            "type",
            "borrowing",
            "session_url",
            "session_id",
            "money_to_pay",
        ):
            self.assertTrue(serializer.fields[field].read_only)
