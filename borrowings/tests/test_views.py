from datetime import timedelta
from decimal import Decimal
from unittest.mock import patch, MagicMock

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from rest_framework import status
from rest_framework.test import APIClient

from books.models import Book
from borrowings.models import Borrowing
from borrowings.serializers import (
    BorrowingDetailSerializer,
    BorrowingListSerializer,
)
from payments.models import Payment

BORROWINGS_URL = reverse("borrowings:borrowing-list")


def detail_url(borrowing_id):
    return reverse(
        "borrowings:borrowing-detail",
        args=[borrowing_id],
    )


def sample_book(**params):
    defaults = {
        "title": "The Hobbit",
        "author": "J.R.R. Tolkien",
        "cover": Book.CoverType.HARD,
        "inventory": 5,
        "daily_fee": Decimal("1.50"),
    }
    defaults.update(params)

    return Book.objects.create(**defaults)


def sample_borrowing(user, **params):
    book = sample_book()

    defaults = {
        "book": book,
        "expected_return_date": timezone.now().date() + timedelta(days=7),
    }
    defaults.update(params)

    return Borrowing.objects.create(user=user, **defaults)


class UnauthenticatedBorrowingAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_borrowing_list_unauthorized(self):
        response = self.client.get(BORROWINGS_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_borrowing_detail_unauthorized(self):
        borrowing = sample_borrowing(
                user=get_user_model().objects.create_user(
                email="user@test.com",
                password="testpassword123",
            )
        )

        response = self.client.get(detail_url(borrowing.id))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_borrowing_unauthorized(self):
        book = sample_book()

        payload = {
            "book": book.id,
            "expected_return_date": timezone.now().date() + timedelta(days=7),
        }

        response = self.client.post(BORROWINGS_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedBorrowingAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.user = get_user_model().objects.create_user(
            email="user@test.com",
            password="testpassword123",
        )

        self.client.force_authenticate(self.user)

        self.stripe_patcher = patch(
            "payments.stripe_service.stripe.checkout.Session.create"
        )
        mock_session_create = self.stripe_patcher.start()
        mock_session_create.return_value = MagicMock(
            url="https://checkout.stripe.com/c/pay/cs_test_fake",
            id="cs_test_fake",
        )
        self.addCleanup(self.stripe_patcher.stop)

    def test_borrowing_list(self):
        borrowing = sample_borrowing(user=self.user)

        response = self.client.get(BORROWINGS_URL)

        serializer = BorrowingListSerializer(borrowing)

        self.assertEqual(response.status_code,status.HTTP_200_OK)

        self.assertIn(serializer.data, response.data)

    def test_borrowing_detail(self):
        borrowing = sample_borrowing(user=self.user)

        response = self.client.get(detail_url(borrowing.id))

        serializer = BorrowingDetailSerializer(borrowing)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(response.data, serializer.data)

    def test_borrowing_list_contains_multiple_borrowings(self):
        borrowing1 = sample_borrowing(user=self.user)

        borrowing2 = sample_borrowing(
            user=self.user,
            book=sample_book(title="The Hobbit 2"),
        )

        response = self.client.get(BORROWINGS_URL)

        serializer1 = BorrowingListSerializer(borrowing1)
        serializer2 = BorrowingListSerializer(borrowing2)

        self.assertEqual(response.status_code, status.HTTP_200_OK,)
        self.assertEqual(len(response.data), 2)

        self.assertIn(serializer1.data, response.data)
        self.assertIn(serializer2.data, response.data)

    def test_borrowing_detail_contains_full_book_information(self):
        book = sample_book()

        borrowing = sample_borrowing(
            user=self.user,
            book=book,
        )

        response = self.client.get(detail_url(borrowing.id))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(response.data["book"]["title"], "The Hobbit")
        self.assertEqual(response.data["book"]["author"], "J.R.R. Tolkien")
        self.assertEqual(response.data["book"]["cover"], book.cover)
        self.assertEqual(response.data["book"]["inventory"], 5)
        self.assertEqual(response.data["book"]["daily_fee"], "1.50")
        self.assertEqual( response.data["user"]["email"], self.user.email)

    def test_borrowing_detail_not_found(self):
        response = self.client.get(detail_url(99999))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_borrowing_successful(self):
        book = sample_book(inventory=5)

        payload = {
            "book": book.id,
            "expected_return_date": timezone.now().date() + timedelta(days=7),
        }

        response = self.client.post(BORROWINGS_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        borrowing = Borrowing.objects.get(id=response.data["id"])

        self.assertEqual(borrowing.user, self.user)
        self.assertEqual(borrowing.book, book)
        self.assertEqual(
            borrowing.expected_return_date,
            timezone.now().date() + timedelta(days=7),
        )

        book.refresh_from_db()

        self.assertEqual(book.inventory, 4)

    def test_create_borrowing_creates_stripe_payment(self):
        book = sample_book(inventory=5, daily_fee=Decimal("1.50"))

        payload = {
            "book": book.id,
            "expected_return_date": timezone.now().date() + timedelta(days=7),
        }

        response = self.client.post(BORROWINGS_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        borrowing = Borrowing.objects.get(id=response.data["id"])
        payment = Payment.objects.get(borrowing=borrowing)

        self.assertEqual(payment.status, Payment.Status.PENDING)
        self.assertEqual(payment.type, Payment.Type.PAYMENT)
        self.assertEqual(payment.money_to_pay, Decimal("10.50"))
        self.assertEqual(payment.session_url, "https://checkout.stripe.com/c/pay/cs_test_fake")
        self.assertEqual(payment.session_id, "cs_test_fake")

    def test_create_borrowing_when_inventory_zero(self):
        book = sample_book(inventory=0)

        payload = {
            "book": book.id,
            "expected_return_date": timezone.now().date() + timedelta(days=7),
        }

        response = self.client.post(BORROWINGS_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST,)

        self.assertFalse(Borrowing.objects.filter(book=book).exists())

        book.refresh_from_db()

        self.assertEqual(book.inventory, 0)

    def test_create_user_is_attached_automatically(self):
        another_user = get_user_model().objects.create_user(
            email="another@test.com",
            password="testpassword123",
        )

        book = sample_book()

        payload = {
            "book": book.id,
            "expected_return_date": (timezone.now().date() + timedelta(days=7)),
            "user": another_user.id,
        }

        response = self.client.post(BORROWINGS_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        borrowing = Borrowing.objects.get(id=response.data["id"])

        self.assertEqual(borrowing.user, self.user)

    def test_create_borrowing_with_invalid_book(self):
        payload = {
            "book": 999999,
            "expected_return_date": timezone.now().date() + timedelta(days=7),
        }

        response = self.client.post(BORROWINGS_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertFalse(Borrowing.objects.exists())

    def test_create_borrowing_with_invalid_expected_return_date(self):
        book = sample_book()

        payload = {
            "book": book.id,
            "expected_return_date": timezone.now().date() - timedelta(days=1),
        }

        response = self.client.post(BORROWINGS_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertFalse(Borrowing.objects.exists())

        book.refresh_from_db()

        self.assertEqual(book.inventory, 5)

    def test_update_borrowing_not_allowed(self):
        borrowing = sample_borrowing(user=self.user)

        response = self.client.patch(
            detail_url(borrowing.id),
            {"actual_return_date": timezone.now().date()},
        )

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete_borrowing_not_allowed(self):
        borrowing = sample_borrowing(user=self.user)

        response = self.client.delete(detail_url(borrowing.id))

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
