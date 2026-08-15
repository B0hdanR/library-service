from drf_spectacular.utils import extend_schema_view, extend_schema
from rest_framework import viewsets

from borrowings.models import Borrowing
from borrowings.serializers import (
    BorrowingListSerializer,
    BorrowingDetailSerializer,
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
)
class BorrowingViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Borrowing.objects.select_related("book", "user")
    serializer_class = BorrowingListSerializer

    def get_serializer_class(self):
        if self.action == "retrieve":
            return BorrowingDetailSerializer
        return BorrowingListSerializer
