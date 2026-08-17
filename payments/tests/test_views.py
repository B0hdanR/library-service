from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from rest_framework import status
from rest_framework.test import APIClient

from payments.models import Payment
from payments.serializers import PaymentListSerializer, PaymentDetailSerializer
from payments.tests.helpers import sample_borrowing, sample_book, sample_payment


PAYMENTS_URL = reverse("payments:payment-list")


def detail_url(payment_id):
    return reverse(
        "payments:payment-detail",
        args=[payment_id],
    )


class UnauthenticatedPaymentAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_payment_list_unauthorized(self):
        response = self.client.get(PAYMENTS_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_payment_detail_unauthorized(self):
        user = get_user_model().objects.create_user(
            email="user@test.com",
            password="testpassword123",
        )

        borrowing = sample_borrowing(user=user)

        payment = sample_payment(borrowing=borrowing)

        response = self.client.get(detail_url(payment.id))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedPaymentAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.user = get_user_model().objects.create_user(
            email="user@test.com",
            password="testpassword123",
        )

        self.other_user = get_user_model().objects.create_user(
            email="other@test.com",
            password="testpassword123",
        )

        self.client.force_authenticate(user=self.user)

    def test_payment_list_contains_only_current_user_payments(self):
        own_borrowing = sample_borrowing(user=self.user)
        own_payment = sample_payment(borrowing=own_borrowing)

        other_borrowing = sample_borrowing(user=self.other_user)
        other_payment = sample_payment(borrowing=other_borrowing)

        response = self.client.get(PAYMENTS_URL)
        serializer = PaymentListSerializer(own_payment)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertIn(serializer.data, response.data)

        self.assertNotIn(other_payment.id, [payment["id"] for payment in response.data])

    def test_payment_detail_allowed_for_own_payment(self):
        borrowing = sample_borrowing(user=self.user)
        payment = sample_payment(borrowing=borrowing)

        response = self.client.get(detail_url(payment.id))
        serializer = PaymentDetailSerializer(payment)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(response.data, serializer.data)

    def test_payment_detail_for_other_user_returns_404(self):
        borrowing = sample_borrowing(user=self.other_user)
        payment = sample_payment(borrowing=borrowing)

        response = self.client.get(detail_url(payment.id))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_payment_list_contains_multiple_own_payments(self):
        borrowing1 = sample_borrowing(user=self.user,)
        borrowing2 = sample_borrowing(
            user=self.user,
            book=sample_book(title="The Hobbit 2"),
            expected_return_date=(timezone.now().date() + timedelta(days=10)),
        )

        payment1 = sample_payment(borrowing=borrowing1)
        payment2 = sample_payment(
            borrowing=borrowing2,
            money_to_pay=Decimal("15.00"),
        )

        response = self.client.get(PAYMENTS_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(len(response.data), 2)
        self.assertIn(PaymentListSerializer(payment1).data, response.data)
        self.assertIn(PaymentListSerializer(payment2).data, response.data)

    def test_payment_create_not_allowed(self):
        response = self.client.post(PAYMENTS_URL, {})

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_payment_update_not_allowed(self):
        borrowing = sample_borrowing(user=self.user)
        payment = sample_payment(borrowing=borrowing)

        response = self.client.patch(
            detail_url(payment.id),
            {"status": Payment.Status.PAID},
        )

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_payment_delete_not_allowed(self):
        borrowing = sample_borrowing(user=self.user)
        payment = sample_payment(borrowing=borrowing)

        response = self.client.delete(detail_url(payment.id))

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class AdminPaymentAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.admin = get_user_model().objects.create_user(
            email="admin@test.com",
            password="testpassword123",
            is_staff=True,
        )

        self.user = get_user_model().objects.create_user(
            email="user@test.com",
            password="testpassword123",
        )

        self.client.force_authenticate(user=self.admin)

    def test_admin_can_see_all_payments(self):
        user_borrowing = sample_borrowing(user=self.user)
        user_payment = sample_payment(borrowing=user_borrowing)

        admin_borrowing = sample_borrowing(user=self.admin)
        admin_payment = sample_payment(borrowing=admin_borrowing)

        response = self.client.get(PAYMENTS_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertIn(PaymentListSerializer(user_payment).data, response.data)
        self.assertIn(PaymentListSerializer(admin_payment).data, response.data)

    def test_admin_can_retrieve_any_payment(self):
        borrowing = sample_borrowing(user=self.user)
        payment = sample_payment(borrowing=borrowing)

        response = self.client.get(detail_url(payment.id))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(response.data, PaymentDetailSerializer(payment).data)

    def test_admin_cannot_create_payment(self):
        response = self.client.post(PAYMENTS_URL, {})

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
