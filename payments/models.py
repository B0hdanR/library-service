from django.db import models

from borrowings.models import Borrowing


class Payment(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        PAID = "PAID", "Paid"

    class Type(models.TextChoices):
        PAYMENT = "PAYMENT", "Payment"
        FINE = "FINE", "Fine"

    status = models.CharField(
        max_length=10,
        choices=Status.choices,  # noqa
        default=Status.PENDING,
    )
    type = models.CharField(
        max_length=10,
        choices=Type.choices,  # noqa
        default=Type.PAYMENT,
    )
    borrowing = models.ForeignKey(
        Borrowing,
        on_delete=models.PROTECT,
        related_name="payments",
    )
    session_url = models.URLField(max_length=255)
    session_id = models.CharField(max_length=255)
    money_to_pay = models.DecimalField(
        max_digits=8,
        decimal_places=2,
    )

    class Meta:
        ordering = ["-id"]

    def __str__(self):
        return f"{self.type} - {self.status} ({self.money_to_pay} USD)"
