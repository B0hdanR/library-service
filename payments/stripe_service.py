import stripe
from django.conf import settings

from payments.models import Payment

stripe.api_key = settings.STRIPE_SECRET_KEY


def calculate_borrowing_total_price(borrowing):
    days = (borrowing.expected_return_date - borrowing.borrow_date).days
    return days * borrowing.book.daily_fee


def create_stripe_session(borrowing):
    total_price = calculate_borrowing_total_price(borrowing)

    session = stripe.checkout.Session.create(
        line_items=[
            {
                "price_data": {
                    "currency": "usd",
                    "product_data": {
                        "name": f"Borrowing of '{borrowing.book.title}'",
                    },
                    "unit_amount": int(total_price * 100),
                },
                "quantity": 1,
            }
        ],
        mode="payment",
        success_url="http://localhost:8000/api/payments/success/",
        cancel_url="http://localhost:8000/api/payments/cancel/",
    )

    return Payment.objects.create(
        status=Payment.Status.PENDING,
        type=Payment.Type.PAYMENT,
        borrowing=borrowing,
        session_url=session.url,
        session_id=session.id,
        money_to_pay=total_price,
    )
