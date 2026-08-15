from drf_spectacular.utils import extend_schema_view, extend_schema
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
        description="Retrieve a list of borrowings.",
    ),
    retrieve=extend_schema(
        tags=["Borrowings"],
        description="Retrieve detailed information about a specific borrowing.",
    ),
    create=extend_schema(
        tags=["Borrowings"],
        description=(
            "Create a new borrowing for the authenticated user. "
            "The book inventory is decreased by one."
        ),
    ),
)
class BorrowingViewSet(viewsets.ModelViewSet):
    queryset = Borrowing.objects.select_related("book", "user")
    serializer_class = BorrowingListSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "post", "head", "options"]

    def get_serializer_class(self):
        if self.action == "create":
            return BorrowingCreateSerializer

        if self.action == "retrieve":
            return BorrowingDetailSerializer

        return BorrowingListSerializer
