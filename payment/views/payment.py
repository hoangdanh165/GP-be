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
from base.utils.custom_pagination import CustomPagination, CustomPaginationPayment
from ..models.payment import Payment
from django.db.models import Q
from django.utils.dateparse import parse_date
from functools import reduce
import operator

from ..serializers.payment import (
    PaymentSerializer,
    PaymentDetailSerializer,
    PaymentUpdateSerializer,
    PaymentListSerializer,
)
from service.models.appointment import Appointment
from ..vnpay import vnpay
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


def get_client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip


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

                appointment = payment.appointment
                appointment.invoice_created = True
                appointment.save(update_fields=["invoice_created"])

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

    @action(
        methods=["patch"],
        url_path="update-status",
        detail=False,
        permission_classes=[IsAuthenticated],
        renderer_classes=[renderers.JSONRenderer],
    )
    def update_status(self, request):
        appointment_id = request.data.get("appointment_id")
        new_status = request.data.get("status")

        if not appointment_id or not new_status:
            return Response(
                {"error": "Missing appointment_id or status"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        valid_statuses = [choice[0] for choice in Payment.PaymentStatus.choices]
        if new_status not in valid_statuses:
            return Response(
                {"error": f"Invalid status. Must be one of: {valid_statuses}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            appointment = get_object_or_404(Appointment, id=appointment_id)
            payment = Payment.objects.filter(appointment=appointment).first()

            if not payment:
                return Response(
                    {"error": "No payment found for this appointment"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            payment.status = new_status
            payment.save()

            serializer = PaymentDetailSerializer(payment)
            return Response(
                {"message": "Status updated successfully", "data": serializer.data}
            )

        except Exception as e:
            return Response(
                {"error": f"Something went wrong: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(
        methods=["get"],
        url_path="get-by-appointment",
        detail=False,
        permission_classes=[IsAuthenticated],
        renderer_classes=[renderers.JSONRenderer],
    )
    def get_by_appointment(self, request):
        appointment_id = request.query_params.get("appointment_id")
        if not appointment_id:
            return Response(
                {"error": "Missing appointment_id"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            appointment = get_object_or_404(Appointment, id=appointment_id)
            payment = Payment.objects.filter(appointment=appointment).first()
            if not payment:
                return Response(
                    {"error": "No payment found for this appointment"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            serializer = PaymentDetailSerializer(payment)
            return Response(
                {"data": serializer.data},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"error": f"Something went wrong: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(
        methods=["get"],
        url_path="all",
        detail=False,
        permission_classes=[AllowAny],
        renderer_classes=[renderers.JSONRenderer],
    )
    def get_all_payments(self, request):
        try:
            payments = Payment.objects.all().order_by("-create_at")

            search = request.query_params.get("search")
            status_filter = request.query_params.get("status")
            method_filter = request.query_params.get("payment_method")
            start_date_str = request.query_params.get("start_date")
            end_date_str = request.query_params.get("end_date")

            search_fields = [
                "invoice_id",
                "transaction_id",
                "note",
                "appointment__id",
                "appointment__customer__full_name",
            ]

            if search:
                query = reduce(
                    operator.or_,
                    [Q(**{f"{field}__icontains": search}) for field in search_fields],
                )
                payments = payments.filter(query)

            if status_filter:
                payments = payments.filter(status=status_filter)

            if method_filter:
                payments = payments.filter(method=method_filter)

            if start_date_str:
                start_date = parse_date(start_date_str)
                if start_date:
                    payments = payments.filter(create_at__date__gte=start_date)

            if end_date_str:
                end_date = parse_date(end_date_str)
                if end_date:
                    payments = payments.filter(create_at__date__lte=end_date)

            paginator = CustomPaginationPayment()
            paginated_payments = paginator.paginate_queryset(payments, request)

            serializer = PaymentDetailSerializer(paginated_payments, many=True)

            return paginator.get_paginated_response({"data": serializer.data})

        except Exception as e:
            return Response(
                {"error": f"Something went wrong: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(
        methods=["post"],
        url_path="create-url",
        detail=False,
        permission_classes=[IsAuthenticated],
        renderer_classes=[renderers.JSONRenderer],
    )
    def payment(self, request):
        try:
            data = request.data

            order_type = data.get("order_type", "billpayment")
            order_id = data.get("order_id")
            amount = int(float(data.get("amount")))

            order_desc = data.get("order_desc")
            bank_code = data.get("bank_code", "")
            language = data.get("language", "vn")

            ipaddr = get_client_ip(request)

            vnp = vnpay()
            vnp.requestData["vnp_Version"] = "2.1.0"
            vnp.requestData["vnp_Command"] = "pay"
            vnp.requestData["vnp_TmnCode"] = settings.VNPAY_TMN_CODE
            vnp.requestData["vnp_Amount"] = amount * 100
            vnp.requestData["vnp_CurrCode"] = "VND"
            vnp.requestData["vnp_TxnRef"] = order_id
            vnp.requestData["vnp_OrderInfo"] = order_desc
            vnp.requestData["vnp_OrderType"] = order_type
            vnp.requestData["vnp_Locale"] = language or "vn"
            if bank_code:
                vnp.requestData["vnp_BankCode"] = bank_code
            vnp.requestData["vnp_CreateDate"] = timezone.localtime(
                timezone.now()
            ).strftime("%Y%m%d%H%M%S")
            vnp.requestData["vnp_IpAddr"] = ipaddr
            vnp.requestData["vnp_ReturnUrl"] = settings.VNPAY_RETURN_URL

            payment_url = vnp.get_payment_url(
                settings.VNPAY_PAYMENT_URL, settings.VNPAY_HASH_SECRET_KEY
            )

            return Response(
                {"code": "00", "payment_url": payment_url}, status=status.HTTP_200_OK
            )

        except Exception as e:
            logger.exception("Error creating VNPAY URL")
            return Response(
                {"code": "99", "message": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(
        methods=["get"],
        url_path="return",
        detail=False,
        permission_classes=[AllowAny],
        renderer_classes=[renderers.JSONRenderer],
    )
    def payment_return(self, request):
        input_data = request.query_params

        if not input_data:
            return Response(
                {"message": "No query parameters found."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        vnp = vnpay()
        vnp.responseData = input_data.dict()

        try:
            order_id = input_data.get("vnp_TxnRef")
            amount = int(input_data.get("vnp_Amount", 0)) / 100
            order_desc = input_data.get("vnp_OrderInfo")
            transaction_no = input_data.get("vnp_TransactionNo")
            response_code = input_data.get("vnp_ResponseCode")
            pay_date = input_data.get("vnp_PayDate")
            bank_code = input_data.get("vnp_BankCode")
            card_type = input_data.get("vnp_CardType")

            if vnp.validate_response(settings.VNPAY_HASH_SECRET_KEY):
                if response_code == "00":
                    return Response(
                        {
                            "title": "Payment Result",
                            "result": "Success",
                            "order_id": order_id,
                            "amount": amount,
                            "order_description": order_desc,
                            "transaction_no": transaction_no,
                            "pay_date": pay_date,
                            "bank_code": bank_code,
                            "card_type": card_type,
                            "response_code": response_code,
                        },
                        status=status.HTTP_200_OK,
                    )
                else:
                    return Response(
                        {
                            "title": "Payment Result",
                            "result": "Failed",
                            "order_id": order_id,
                            "amount": amount,
                            "order_description": order_desc,
                            "transaction_no": transaction_no,
                            "pay_date": pay_date,
                            "bank_code": bank_code,
                            "card_type": card_type,
                            "response_code": response_code,
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            else:
                return Response(
                    {
                        "title": "Payment Result",
                        "result": "Invalid checksum",
                        "message": "Secure hash verification failed.",
                        "order_id": order_id,
                        "amount": amount,
                        "order_description": order_desc,
                        "transaction_no": transaction_no,
                        "response_code": response_code,
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

        except Exception as e:
            return Response(
                {
                    "message": "An error occurred while processing payment return.",
                    "error": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(
        methods=["get"],
        url_path="ipn",
        detail=False,
        permission_classes=[AllowAny],
        renderer_classes=[renderers.JSONRenderer],
    )
    def payment_ipn(self, request):
        input_data = request.query_params

        if not input_data:
            print("NO INPUT DATA")
            return Response(
                {"RspCode": "99", "Message": "Invalid request"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        vnp = vnpay()
        vnp.responseData = input_data.dict()

        try:
            order_id = input_data.get("vnp_TxnRef")
            amount = input_data.get("vnp_Amount")
            order_desc = input_data.get("vnp_OrderInfo")
            transaction_no = input_data.get("vnp_TransactionNo")
            response_code = input_data.get("vnp_ResponseCode")
            pay_date = input_data.get("vnp_PayDate")
            bank_code = input_data.get("vnp_BankCode")
            card_type = input_data.get("vnp_CardType")

            if not vnp.validate_response(settings.VNPAY_HASH_SECRET_KEY):
                print("INVALID SIGNATURE")
                return Response(
                    {"RspCode": "97", "Message": "Invalid signature"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # TODO: Replace with your real DB logic here:
            # Check if order is already updated
            first_time_update = True

            if not first_time_update:
                return Response(
                    {"RspCode": "02", "Message": "Order already updated"},
                    status=status.HTTP_200_OK,
                )

            try:
                payment = get_object_or_404(Payment, invoice_id=order_id)

                if payment.status != Payment.PaymentStatus.PENDING:
                    return Response(
                        {"RspCode": "02", "Message": "Order already updated"},
                        status=status.HTTP_200_OK,
                    )

                correct_amount = str(int(payment.amount * 100)) == amount
                if not correct_amount:
                    return Response(
                        {"RspCode": "04", "Message": "Invalid amount"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                if response_code == "00":
                    print("Payment success")

                    payment.status = Payment.PaymentStatus.PAID
                    payment.transaction_id = transaction_no
                    payment.paid_at = timezone.now()

                    node_server = os.getenv("NODE_JS_HOST", "http://localhost:5000")
                    node_payment_api = "/api/v1/payments/"
                    node_url = node_server + node_payment_api
                    formData = {"invoice_id": order_id, "status": "paid"}

                    try:
                        res = requests.post(node_url, json={"formData": formData})
                        print("Sent data to Node.js:", res.status_code, res.text)
                    except requests.RequestException as e:
                        print("Failed to send to Node.js:", str(e))

                else:
                    print(f"Payment failed with code: {response_code}")

                    payment.status = Payment.PaymentStatus.FAILED
                    payment.transaction_id = transaction_no
                    payment.note = f"Failed with code {response_code} at {pay_date}"

                payment.save()

            except Payment.DoesNotExist:
                return Response(
                    {"RspCode": "01", "Message": "Order not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            return Response(
                {"RspCode": "00", "Message": "Confirm success"},
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {"RspCode": "99", "Message": f"Internal server error: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
