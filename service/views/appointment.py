import os
from google.oauth2 import id_token
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
from ..models.appointment import Appointment
from ..models.appointment_service import AppointmentService
from ..serializers.appointment import (
    AppointmentSerializer,
    AppointmentDetailSerializer,
    AppointmentUpdateSerializer,
)
from ..services.appoinment import (
    send_appointment_reminder_email,
    send_vehicle_ready_email,
)
from datetime import datetime


class AppointmentViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.all().order_by("id")

    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "list":
            return AppointmentSerializer
        elif self.action == "retrieve":
            return AppointmentDetailSerializer
        elif self.action == "create":
            return AppointmentUpdateSerializer
        elif self.action in ["update", "partial_update"]:
            return AppointmentUpdateSerializer
        return AppointmentDetailSerializer

    # pagination_class = CustomPagination

    def get(self, request):
        try:
            appointment = Appointment.objects.all()
            serializer_class = self.get_serializer_class()
            serializer = serializer_class(appointment, many=True)

            return Response(serializer.data, status=status.HTTP_200_OK)

        except Appointment.DoesNotExist:
            return Response(
                {"detail": "Appointment not found."}, status=status.HTTP_404_NOT_FOUND
            )

    @action(
        methods=["put"],
        url_path="update",
        detail=True,
        permission_classes=[IsAuthenticated],
        renderer_classes=[renderers.JSONRenderer],
    )
    def manual_update(self, request, pk=None):
        try:
            appointment = get_object_or_404(Appointment, pk=pk)

            serializer = AppointmentUpdateSerializer(
                appointment, data=request.data, partial=True
            )

            if serializer.is_valid():
                serializer.save()
                return Response(
                    {
                        "detail": "Appointment updated successfully!",
                        "data": serializer.data,
                    },
                    status=status.HTTP_200_OK,
                )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Appointment.DoesNotExist:
            return Response(
                {"error": "Appointment not found."}, status=status.HTTP_404_NOT_FOUND
            )

    @action(
        methods=["get"],
        url_path="details",
        detail=True,
        permission_classes=[IsAuthenticated],
        renderer_classes=[renderers.JSONRenderer],
    )
    def get_detail(self, request, pk=None):
        try:
            appointment = get_object_or_404(self.get_queryset(), pk=pk)
            serializer_class = self.get_serializer_class()
            serializer = serializer_class(appointment)
            return Response(serializer.data)
        except Appointment.DoesNotExist:
            return Response(
                {"error": "Appointment not found."}, status=status.HTTP_404_NOT_FOUND
            )

    @action(
        methods=["post"],
        url_path="create-reminder",
        detail=False,
        permission_classes=[AllowAny],
        renderer_classes=[renderers.JSONRenderer],
    )
    def create_reminder(self, request):
        appointment_id = request.data.get("id")
        type = request.data.get("type")
        vehicle_ready_time_raw = request.data.get("vehicle_ready_time")
        formatted_ready_time = None

        if vehicle_ready_time_raw:
            try:
                dt = datetime.fromisoformat(vehicle_ready_time_raw)

                formatted_ready_time = dt.strftime("%I:%M %p, %B %d, %Y")
            except Exception as e:
                return Response(
                    {"error": f"Invalid vehicle_ready_time format: {str(e)}"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        reminder_type = request.data.get("reminder_type")

        if not appointment_id or not reminder_type:
            return Response(
                {"error": "Missing required parameters: id and reminder_type"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        appointment = get_object_or_404(Appointment, id=appointment_id)

        user = appointment.customer

        appointment_time = appointment.get_date().strftime(
            "%I:%M %p, %B %d, %Y"
        )  # 3:30 PM, April 15, 2025

        print("APPOJ", appointment.get_date())
        appointment_services = AppointmentService.objects.filter(
            appointment=appointment
        )

        services = (
            ", ".join(
                [
                    appointment_service.service.name
                    for appointment_service in appointment_services
                ]
            )
            or "General maintenance and more."
        )

        REMINDER_CONFIG = {
            "APPOINTMENT_REMINDER_B1H": {
                "field": "reminded_before_1h",
                "email_params": {
                    "template": "service/email/appointment_reminder_1h.html",
                    "user": user,
                    "appointment_time": appointment_time,
                    "services": services,
                },
                "success_message": "1-hour reminder email sent successfully",
            },
            "APPOINTMENT_REMINDER_B1D": {
                "field": "reminded_before_1d",
                "email_params": {
                    "template": "service/email/appointment_reminder_1d.html",
                    "user": user,
                    "appointment_time": appointment_time,
                    "services": services,
                },
                "success_message": "1-day reminder email sent successfully",
            },
            "VEHICLE_READY_REMINDER": {
                "field": "reminded_vehicle_ready",
                "email_params": {
                    "template": "service/email/vehicle_ready_reminder.html",
                    "user": user,
                    "vehicle_ready_time": formatted_ready_time,
                    "services": services,
                },
                "success_message": "Vehicle ready reminder email sent successfully",
            },
        }

        config = REMINDER_CONFIG.get(reminder_type)
        if not config:
            return Response(
                {"error": f"Unsupported reminder_type: {reminder_type}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if getattr(appointment, config["field"]):
            return Response(
                {"detail": f"{reminder_type} already sent for this appointment"},
                status=status.HTTP_200_OK,
            )

        try:
            if config["email_params"].get("vehicle_ready_time"):
                send_vehicle_ready_email(**config["email_params"])
            else:
                send_appointment_reminder_email(**config["email_params"])

            setattr(appointment, config["field"], True)

            appointment.save(update_fields=[config["field"]])

            return Response(
                {"message": config["success_message"]}, status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"error": f"Failed to send email: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
