from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from books.models import Book
from books.serializers import BookSerializer

BOOKS_URL = reverse("books:book-list")

def detail_url(book_id):
    return reverse("books:book-detail", args=[book_id])

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


class UnauthenticatedBookAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_book_list_allowed(self):
        sample_book()

        response = self.client.get(BOOKS_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_book_detail_allowed(self):
        book = sample_book()

        response = self.client.get(detail_url(book.id))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_book_create_forbidden(self):
        payload = {
            "title": "The Hobbit",
            "author": "J.R.R. Tolkien",
            "cover": Book.CoverType.HARD,
            "inventory": 5,
            "daily_fee": Decimal("1.50"),
        }

        response = self.client.post(BOOKS_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_book_update_unauthorized(self):
        book = sample_book()

        response = self.client.patch(
            detail_url(book.id),
            {"title": "New title"},
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_book_delete_unauthorized(self):
        book = sample_book()

        response = self.client.delete(detail_url(book.id))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedBookAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.user = get_user_model().objects.create_user(
            email="user@test.com",
            password="testpassword123",
        )

        self.client.force_authenticate(self.user)

    def test_book_list_allowed(self):
        sample_book()
        sample_book(title="The Hobbit 2")

        response = self.client.get(BOOKS_URL)

        books = Book.objects.all()
        serializer = BookSerializer(books, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_book_detail_allowed(self):
        book = sample_book()

        response = self.client.get(detail_url(book.id))

        serializer = BookSerializer(book)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_book_create_forbidden(self):
        payload = {
            "title": "The Hobbit",
            "author": "J.R.R. Tolkien",
            "cover": Book.CoverType.HARD,
            "inventory": 5,
            "daily_fee": Decimal("1.50")
        }

        response = self.client.post(BOOKS_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_book_update_forbidden(self):
        book = sample_book()

        response = self.client.patch(
            detail_url(book.id),
            {"title": "New title"},
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_book_delete_forbidden(self):
        book = sample_book()

        response = self.client.delete(detail_url(book.id))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AdminBookAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.admin = get_user_model().objects.create_user(
            email="admin@test.com",
            password="testpassword123",
            is_staff=True,
        )

        self.client.force_authenticate(self.admin)

    def test_book_create_successful(self):
        payload = {
            "title": "The Hobbit",
            "author": "J.R.R. Tolkien",
            "cover": Book.CoverType.HARD,
            "inventory": 5,
            "daily_fee": Decimal("1.50")
        }

        response = self.client.post(BOOKS_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        book = Book.objects.get(id=response.data["id"])

        for key in payload:
            self.assertEqual(payload[key], getattr(book, key))

    def test_book_update_successful(self):
        book = sample_book()

        response = self.client.patch(
            detail_url(book.id),
            {
                "title": "Updated title",
                "inventory": 10,
            },
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        book.refresh_from_db()

        self.assertEqual(book.title, "Updated title")
        self.assertEqual(book.inventory, 10)

    def test_book_delete_successful(self):
        book = sample_book()

        response = self.client.delete(detail_url(book.id))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.assertFalse(Book.objects.filter(id=book.id).exists())
