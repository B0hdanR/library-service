from decimal import Decimal

from django.test import TestCase

from books.models import Book
from books.serializers import BookSerializer


class BookSerializerTests(TestCase):

    def test_valid_book_data(self):
        data = {
            "title": "The Hobbit",
            "author": "J.R.R. Tolkien",
            "cover": Book.CoverType.HARD,
            "inventory": 5,
            "daily_fee": Decimal("1.50")
        }

        serializer = BookSerializer(data=data)

        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(serializer.data["title"], "The Hobbit")
        self.assertEqual(serializer.data["author"], "J.R.R. Tolkien")
        self.assertEqual(serializer.data["cover"], Book.CoverType.HARD)
        self.assertEqual(serializer.data["inventory"], 5)
        self.assertEqual(serializer.data["daily_fee"], "1.50")

    def test_inventory_cannot_be_negative(self):
        data = {
            "title": "The Hobbit",
            "author": "J.R.R. Tolkien",
            "cover": Book.CoverType.HARD,
            "inventory": -1,
            "daily_fee": Decimal("1.50")
        }

        serializer = BookSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn("inventory", serializer.errors)

    def test_daily_fee_cannot_be_negative(self):
        data = {
            "title": "The Hobbit",
            "author": "J.R.R. Tolkien",
            "cover": Book.CoverType.HARD,
            "inventory": 5,
            "daily_fee": Decimal("-1.50")
        }

        serializer = BookSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn("daily_fee", serializer.errors)
