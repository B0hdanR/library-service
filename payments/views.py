from drf_spectacular.utils import (
    extend_schema,
    extend_schema_view,
    OpenApiResponse,
    OpenApiExample,
)
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
        summary="List payments",
        description=(
            "Returns payments belonging to the current user. "
            "Admin users see payments for all users."
        ),
        responses={
            200: PaymentListSerializer(many=True),
            401: OpenApiResponse(description="Authentication credentials were not provided."),
        },
        examples=[
            OpenApiExample(
                "Example response",
                value=[
                    {
                        "id": 1,
                        "status": "PENDING",
                        "type": "PAYMENT",
                        "borrowing_id": 3,
                        "money_to_pay": "10.50",
                    }
                ],
                response_only=True,
            ),
        ],
    ),
    retrieve=extend_schema(
        tags=["Payments"],
        summary="Retrieve a payment",
        description=(
            "Returns detailed information about a specific payment, "
            "including the Stripe session URL and ID. Only the owner "
            "of the related borrowing or an admin can access it."
        ),
        responses={
            200: PaymentDetailSerializer,
            401: OpenApiResponse(description="Authentication credentials were not provided."),
            404: OpenApiResponse(description="Payment not found or not accessible to this user."),
        },
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
