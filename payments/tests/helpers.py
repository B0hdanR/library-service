from datetime import timedelta
from decimal import Decimal

from django.utils import timezone

from books.models import Book
from borrowings.models import Borrowing
from payments.models import Payment


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


def sample_payment(borrowing, **params):
    defaults = {
        "status": Payment.Status.PENDING,
        "type": Payment.Type.PAYMENT,
        "borrowing": borrowing,
        "session_url": "https://checkout.stripe.com/pay/session_test",
        "session_id": "session_test",
        "money_to_pay": Decimal("10.50"),
    }

    defaults.update(params)

    return Payment.objects.create(**defaults)
