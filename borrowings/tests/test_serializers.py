from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from books.models import Book
from borrowings.models import Borrowing
from borrowings.serializers import (
    BorrowingDetailSerializer,
    BorrowingListSerializer,
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
    book = params.pop("book", None) or sample_book()

    defaults = {
        "book": book,
        "expected_return_date": timezone.now().date() + timedelta(days=7),
    }
    defaults.update(params)

    return Borrowing.objects.create(user=user, **defaults)


class BorrowingSerializerTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="user@test.com", password="testpassword123"
        )

    def test_list_serializer_contains_book_title_and_user_email(self):
        borrowing = sample_borrowing(user=self.user)

        serializer = BorrowingListSerializer(borrowing)

        self.assertEqual(serializer.data["book_title"], "The Hobbit")
        self.assertEqual(serializer.data["user_email"], "user@test.com")

    def test_detail_serializer_contains_book_details(self):
        borrowing = sample_borrowing(user=self.user)

        serializer = BorrowingDetailSerializer(borrowing)

        self.assertEqual(
            serializer.data["book"]["title"],
            "The Hobbit",
        )
        self.assertEqual(
            serializer.data["book"]["author"],
            "J.R.R. Tolkien",
        )
        self.assertEqual(
            serializer.data["book"]["cover"],
            Book.CoverType.HARD,
        )
        self.assertEqual(
            serializer.data["book"]["inventory"],
            5,
        )
        self.assertEqual(
            serializer.data["book"]["daily_fee"],
            "1.50",
        )

    def test_detail_serializer_contains_user_details(self):
        borrowing = sample_borrowing(user=self.user)

        serializer = BorrowingDetailSerializer(borrowing)

        self.assertEqual(serializer.data["user"]["id"], self.user.id)
        self.assertEqual(serializer.data["user"]["email"], "user@test.com")
        self.assertEqual(serializer.data["user"]["first_name"], "")
        self.assertEqual(serializer.data["user"]["last_name"], "")
        self.assertFalse(serializer.data["user"]["is_staff"])
