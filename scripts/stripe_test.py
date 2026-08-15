import os
import stripe
from dotenv import load_dotenv

load_dotenv()

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

session = stripe.checkout.Session.create(
    line_items=[{
        "price_data": {
            "currency": "usd",
            "product_data": {
                "name": "The Hobbit 2",
            },
            "unit_amount": 750,
        },
        "quantity": 1,
    }],
    mode="payment",
    success_url="http://localhost:8000/api/payments/success/",
    cancel_url="http://localhost:8000/api/payments/cancel/",
)

print("session.id:", session.id)
print("session.url:", session.url)
