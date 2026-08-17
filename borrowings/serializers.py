from django.db import transaction
from django.utils import timezone
from rest_framework import serializers

from books.models import Book
from books.serializers import BookSerializer
from borrowings.models import Borrowing
from payments.serializers import PaymentDetailSerializer
from payments.stripe_service import create_stripe_session
from users.serializers import UserSerializer


class BorrowingListSerializer(serializers.ModelSerializer):
    book_title = serializers.CharField(source="book.title", read_only=True)
    user_email = serializers.EmailField(source="user.email", read_only=True)

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book_title",
            "user_email",
        )


class BorrowingPaymentSerializer(PaymentDetailSerializer):
    class Meta(PaymentDetailSerializer.Meta):
        fields = tuple(
            field
            for field in PaymentDetailSerializer.Meta.fields
            if field != "borrowing"
        )
        read_only_fields = fields


class BorrowingDetailSerializer(serializers.ModelSerializer):
    book = BookSerializer(read_only=True)
    user = UserSerializer(read_only=True)
    payments = BorrowingPaymentSerializer(many=True, read_only=True)

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
            "user",
            "payments",
        )


class BorrowingCreateSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "expected_return_date",
            "book",
            "user",
        )
        read_only_fields = ("id",)

    @staticmethod
    def validate_expected_return_date(value):
        if value < timezone.now().date():
            raise serializers.ValidationError(
                "Expected return date cannot be in the past."
            )

        return value

    def create(self, validated_data):
        user = validated_data.pop("user")
        book_instance = validated_data.pop("book")

        with transaction.atomic():
            book = Book.objects.select_for_update().get(pk=book_instance.pk)

            if book.inventory == 0:
                raise serializers.ValidationError(
                    {"book": "This book is currently out of stock."}
                )

            book.inventory -= 1
            book.save(update_fields=["inventory"])

            borrowing = Borrowing.objects.create(
                user=user,
                book=book,
                **validated_data,
            )

            create_stripe_session(borrowing)

            return borrowing
