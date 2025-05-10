from ..models.payment import Payment
from rest_framework import serializers
from service.serializers.appointment import AppointmentDetailSerializer


class PaymentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Payment
        fields = [
            "id",
            "invoice_id",
            "method",
            "status",
            "amount",
            "transaction_id",
            "paid_at",
            "note",
            "create_at",
            "update_at",
        ]


class PaymentDetailSerializer(serializers.ModelSerializer):
    appointment = AppointmentDetailSerializer()

    class Meta:
        model = Payment
        fields = [
            "id",
            "invoice_id",
            "appointment",
            "method",
            "status",
            "amount",
            "transaction_id",
            "paid_at",
            "note",
            "qr_code_url",
            "create_at",
            "update_at",
        ]


class PaymentUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            "appointment",
            "method",
            "amount",
            # "transaction_id",
            "paid_at",
            "note",
        ]
