from django.conf import settings
from django.db import models

from books.models import Book


class Borrowing(models.Model):
    borrow_date = models.DateField(auto_now_add=True)
    expected_return_date = models.DateField()
    actual_return_date = models.DateField(null=True, blank=True)

    book = models.ForeignKey(
        Book,
        on_delete=models.PROTECT,
        related_name="borrowings",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="borrowings",
    )

    class Meta:
        ordering = ["-borrow_date"]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(
                    expected_return_date__gte=models.F("borrow_date")
                ),
                name="expected_return_date_gte_borrow_date",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(actual_return_date__isnull=True)
                    | models.Q(actual_return_date__gte=models.F("borrow_date"))
                ),
                name="actual_return_date_gte_borrow_date",
            ),
        ]

    def __str__(self):
        return f"{self.book.title} - {self.user.email} (borrowed  {self.borrow_date})"
