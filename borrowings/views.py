from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiResponse,
    OpenApiExample,
)
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from borrowings.models import Borrowing
from borrowings.serializers import (
    BorrowingListSerializer,
    BorrowingDetailSerializer,
    BorrowingCreateSerializer,
)


@extend_schema_view(
    list=extend_schema(
        tags=["Borrowings"],
        summary="List borrowings",
        description=(
            "Returns borrowings belonging to the current user. "
            "Admin users see borrowings for all users."
        ),
        responses={
            200: BorrowingListSerializer(many=True),
            401: OpenApiResponse(description="Authentication credentials were not provided."),
        },
    ),
    retrieve=extend_schema(
        tags=["Borrowings"],
        summary="Retrieve a borrowing",
        description=(
            "Returns detailed information about a specific borrowing, "
            "including full book info and any related payments."
        ),
        responses={
            200: BorrowingDetailSerializer,
            401: OpenApiResponse(description="Authentication credentials were not provided."),
            404: OpenApiResponse(description="Borrowing not found or not accessible to this user."),
        },
    ),
    create=extend_schema(
        tags=["Borrowings"],
        summary="Create a borrowing",
        description=(
            "Creates a new borrowing for the authenticated user. "
            "The user field is set automatically from the request and "
            "any value passed for it is ignored. Decreases the book's "
            "inventory by one and automatically creates a Stripe Checkout "
            "Session for payment."
        ),
        request=BorrowingCreateSerializer,
        responses={
            201: BorrowingCreateSerializer,
            400: OpenApiResponse(
                description=(
                    "Validation error - either the book is out of stock "
                    "(inventory is 0) or expected_return_date is in the past."
                )
            ),
            401: OpenApiResponse(description="Authentication credentials were not provided."),
        },
        examples=[
            OpenApiExample(
                "Example request",
                value={
                    "book": 1,
                    "expected_return_date": "2026-08-24",
                },
                request_only=True,
            ),
        ],
    ),
)
class BorrowingViewSet(viewsets.ModelViewSet):
    serializer_class = BorrowingListSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "post", "head", "options"]

    def get_queryset(self):
        queryset = Borrowing.objects.select_related("book", "user").prefetch_related(
            "payments"
        )
        user = self.request.user
        if user.is_staff:
            return queryset
        return queryset.filter(user=user)

    def get_serializer_class(self):
        if self.action == "create":
            return BorrowingCreateSerializer

        if self.action == "retrieve":
            return BorrowingDetailSerializer

        return BorrowingListSerializer
