from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from payments.models import Payment
from payments.serializers import (
    PaymentDetailSerializer,
    PaymentListSerializer,
)


@extend_schema_view(
    list=extend_schema(
        tags=["Payments"],
        description="Retrieve payments available to the current user.",
    ),
    retrieve=extend_schema(
        tags=["Payments"],
        description="Retrieve detailed information about a specific payment.",
    ),
)
class PaymentViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PaymentListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Payment.objects.select_related(
            "borrowing", "borrowing__book", "borrowing__user"
        )
        user = self.request.user

        if user.is_staff:
            return queryset
        return queryset.filter(borrowing__user=user)

    def get_serializer_class(self):
        if self.action == "retrieve":
            return PaymentDetailSerializer
        return PaymentListSerializer
