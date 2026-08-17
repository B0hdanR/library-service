from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from borrowings.models import Borrowing
from borrowings.serializers import (
    BorrowingListSerializer,
    BorrowingDetailSerializer,
    BorrowingCreateSerializer,
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
