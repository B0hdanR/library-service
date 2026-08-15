from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.test import TestCase
from django.utils import timezone

from books.models import Book
from borrowings.models import Borrowing


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


class BorrowingModelTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="user@test.com", password="testpassword123"
        )

    def test_borrowing_creation_successful(self):
        borrowing = sample_borrowing(user=self.user)

        self.assertIsNotNone(borrowing.id)
        self.assertEqual(borrowing.book.title, "The Hobbit")
        self.assertEqual(borrowing.user.email, "user@test.com")
        self.assertEqual(
            borrowing.expected_return_date,
            timezone.now().date() + timedelta(days=7),
        )
        self.assertIsNone(borrowing.actual_return_date)

    def test_borrow_date_created_automatically(self):
        borrowing = sample_borrowing(user=self.user)

        self.assertEqual(borrowing.borrow_date, timezone.now().date())

    def test_actual_return_date_can_be_null(self):
        borrowing = sample_borrowing(user=self.user)

        self.assertIsNone(borrowing.actual_return_date)

    def test_expected_return_date_cannot_be_before_borrow_date(self):
        with self.assertRaises(IntegrityError):
            sample_borrowing(
                user=self.user,
                expected_return_date=timezone.now().date() - timedelta(days=1),
            )

    def test_actual_return_date_cannot_be_before_borrow_date(self):
        with self.assertRaises(IntegrityError):
            sample_borrowing(
                user=self.user,
                actual_return_date=timezone.now().date() - timedelta(days=1),
            )
