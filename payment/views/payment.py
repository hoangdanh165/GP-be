import os
import requests
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, renderers
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status
from django.conf import settings
from django.utils import timezone
from base.utils.custom_pagination import CustomPagination
from ..models.payment import Payment
from ..serializers.payment import (
    PaymentSerializer,
    PaymentDetailSerializer,
    PaymentUpdateSerializer,
)
from service.models.appointment import Appointment


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all().order_by("id")

    permission_classes = [IsAuthenticated]
    serializer_class = PaymentSerializer
    # pagination_class = CustomPagination

    def get_serializer_class(self):
        if self.action == "list":
            return PaymentSerializer
        elif self.action == "retrieve":
            return PaymentDetailSerializer
        elif self.action == ["create", "update"]:
            return PaymentUpdateSerializer
        return PaymentSerializer

    @action(
        methods=["post"],
        url_path="create-invoice",
        detail=False,
        permission_classes=[IsAuthenticated],
        renderer_classes=[renderers.JSONRenderer],
    )
    def create_invoice(self, request):
        data = request.data
        serializer = PaymentUpdateSerializer(data=data)

        if serializer.is_valid():
            try:
                payment = Payment(
                    appointment=serializer.validated_data["appointment"],
                    method=serializer.validated_data["method"],
                    amount=serializer.validated_data["amount"],
                    transaction_id=serializer.validated_data.get("transaction_id"),
                    note=serializer.validated_data.get("note"),
                )
                payment.save()

                response_serializer = PaymentDetailSerializer(payment)
                return Response(
                    {
                        "detail": "Invoice created successfully",
                        "data": response_serializer.data,
                    },
                    status=status.HTTP_201_CREATED,
                )
            except Exception as e:
                return Response(
                    {"error": f"Failed to create invoice: {str(e)}"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            return Response(
                {"error": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
