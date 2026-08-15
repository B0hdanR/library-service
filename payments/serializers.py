from rest_framework import serializers

from payments.models import Payment


class PaymentListSerializer(serializers.ModelSerializer):
    borrowing_id = serializers.IntegerField(source="borrowing.id", read_only=True)

    class Meta:
        model = Payment
        fields = (
            "id",
            "status",
            "type",
            "borrowing_id",
            "money_to_pay",
        )
        read_only_fields = fields


class PaymentDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = (
            "id",
            "status",
            "type",
            "borrowing",
            "session_url",
            "session_id",
            "money_to_pay",
        )
        read_only_fields = fields
