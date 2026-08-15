from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import TestCase

from books.models import Book

def sample_book(**params):
    defaults = {
        "title": "The Hobbit",
        "author": "J.R.R. Tolkien",
        "cover": Book.CoverType.HARD,
        "inventory": 5,
        "daily_fee": Decimal("1.50")
    }
    defaults.update(params)

    return Book.objects.create(**defaults)


class BookModelTests(TestCase):
    def test_create_book(self):
        book = sample_book()

        self.assertEqual(book.title, "The Hobbit")
        self.assertEqual(book.author, "J.R.R. Tolkien")
        self.assertEqual(book.cover, Book.CoverType.HARD)
        self.assertEqual(book.inventory, 5)
        self.assertEqual(book.daily_fee, Decimal("1.50"))

    def test_inventory_cannot_be_negative(self):
        book = Book(
            title="The Hobbit",
            author="J.R.R. Tolkien",
            cover=Book.CoverType.HARD,
            inventory=-1,
            daily_fee=Decimal("1.50"),
        )

        with self.assertRaises(ValidationError):
            book.full_clean()

    def test_daily_fee_cannot_be_negative(self):
        book = Book(
            title="The Hobbit",
            author="J.R.R. Tolkien",
            cover=Book.CoverType.HARD,
            inventory=5,
            daily_fee=Decimal("-1.50"),
        )

        with self.assertRaises(ValidationError):
            book.full_clean()

    def test_cover_choices(self):
        self.assertEqual(
            Book.CoverType.HARD,
            "HARD",
        )
        self.assertEqual(
            Book.CoverType.SOFT,
            "SOFT",
        )

    def test_book_string_representation(self):
        book = sample_book()
        self.assertEqual(str(book), "The Hobbit")
