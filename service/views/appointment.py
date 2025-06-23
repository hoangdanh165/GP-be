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
from django.utils.timezone import now
from datetime import date
from ..serializers.appointment import (
    AppointmentSerializer,
    AppointmentDetailSerializer,
    AppointmentUpdateSerializer,
)
from ..services.appoinment import (
    send_appointment_reminder_email,
    send_vehicle_ready_email,
)
from base.utils.custom_pagination import CustomPaginationAppointment
from functools import reduce
from django.db.models.functions import TruncDate
from django.db.models import Count
from django.db.models import Q
from datetime import timedelta
import operator
from django.utils.dateparse import parse_date

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

    @action(
        methods=["get"],
        url_path="my-appointments",
        detail=False,
        permission_classes=[IsAuthenticated],
        renderer_classes=[renderers.JSONRenderer],
    )
    def my_appointments(self, request):
        user = request.user
        appointments = self.queryset.filter(customer=user).order_by("-create_at")
        serializer = AppointmentDetailSerializer(appointments, many=True)
        return Response(serializer.data)

    @action(
        methods=["get"],
        url_path="all",
        detail=False,
        permission_classes=[IsAuthenticated],
        renderer_classes=[renderers.JSONRenderer],
    )
    def get_all_appointments(self, request):
        try:
            appointments = Appointment.objects.all().order_by("-create_at")

            search = request.query_params.get("search")
            status_filter = request.query_params.get("status")
            vehicle_filter = request.query_params.get("vehicle")
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
                appointments = appointments.filter(query)

            if status_filter:
                appointments = appointments.filter(status=status_filter)

            if vehicle_filter:
                appointments = appointments.filter(
                    vehicle_information__vin__icontains=vehicle_filter
                )

            if start_date_str:
                start_date = parse_date(start_date_str)
                if start_date:
                    appointments = appointments.filter(date__date__gte=start_date)

            if end_date_str:
                end_date = parse_date(end_date_str)
                if end_date:
                    appointments = appointments.filter(date__date__lte=end_date)

            paginator = CustomPaginationAppointment()
            paginated_appointments = paginator.paginate_queryset(appointments, request)

            serializer = AppointmentDetailSerializer(paginated_appointments, many=True)

            return paginator.get_paginated_response({"data": serializer.data})

        except Exception as e:
            return Response(
                {"error": f"Something went wrong: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(
        methods=["get"],
        url_path="stats/appointments-last-30-days",
        detail=False,
        permission_classes=[IsAuthenticated],
        renderer_classes=[renderers.JSONRenderer],
    )
    def appointments_last_30_days(self, request):
        today = now().date()
        start_date = today - timedelta(days=29)

        valid_statuses = ["completed", "confirmed", "processing", "pending"]

        appointments_per_day = (
            Appointment.objects.filter(
                create_at__date__gte=start_date,
                status__in=valid_statuses,
            )
            .annotate(day=TruncDate("create_at"))
            .values("day")
            .annotate(count=Count("id"))
            .order_by("day")
        )

        date_to_count = {entry["day"]: entry["count"] for entry in appointments_per_day}

        data = []
        for i in range(30):
            day = start_date + timedelta(days=i)
            data.append(date_to_count.get(day, 0))

        return Response(
            {
                "title": "Appointments",
                "value": sum(data),
                "interval": "Last 30 days",
                "trend": "up" if data[-1] > data[0] else "down",
                "data": data,
            }
        )

    @action(
        methods=["get"],
        url_path="stats/popular-time-slots",
        detail=False,
        permission_classes=[IsAuthenticated],
        renderer_classes=[renderers.JSONRenderer],
    )
    def popular_time_slots(self, request):
        queryset = Appointment.objects.all()

        time_slots = [
            ("08:00", "09:59"),
            ("10:00", "11:59"),
            ("13:30", "15:29"),
            ("15:30", "17:30"),
        ]

        slot_labels = [f"{start} - {end}" for start, end in time_slots]
        data = [0 for _ in time_slots]

        for idx, (start_str, end_str) in enumerate(time_slots):
            start_hour = datetime.strptime(start_str, "%H:%M").time()
            end_hour = datetime.strptime(end_str, "%H:%M").time()

            count = queryset.filter(
                date__time__gte=start_hour,
                date__time__lte=end_hour,
            ).count()

            data[idx] = count

        response = {
            "xAxis": {
                "scaleType": "band",
                "categoryGapRatio": 0.5,
                "data": slot_labels,
            },
            "series": [
                {
                    "id": "appointments",
                    "label": "Appointments",
                    "data": data,
                    "stack": "A",
                }
            ],
        }

        return Response(response)

    @action(
        methods=["get"],
        url_path="stats/popular-car-brands",
        detail=False,
        permission_classes=[IsAuthenticated],
        renderer_classes=[renderers.JSONRenderer],
    )
    def popular_car_brands(self, request):
        appointments = Appointment.objects.all()

        stats = {}
        for appt in appointments:
            vehicle = appt.vehicle_information or {}
            brand = vehicle.get("brand", "Unknown")
            name = vehicle.get("name", "Unknown")

            if brand not in stats:
                stats[brand] = {}

            if name not in stats[brand]:
                stats[brand][name] = 0

            stats[brand][name] += 1

        response_data = [
            {
                "brand": brand,
                "total": sum(types.values()),
                "types": [
                    {"name": name, "count": count} for name, count in types.items()
                ],
            }
            for brand, types in stats.items()
        ]

        return Response(response_data)

    @action(
        methods=["get"],
        url_path="stats/count-by-status",
        detail=False,
        permission_classes=[IsAuthenticated],
        renderer_classes=[renderers.JSONRenderer],
    )
    def count_by_status(self, request):
        from_date = request.query_params.get("from")
        to_date = request.query_params.get("to")

        try:
            from_date = parse_date(from_date) or date.today().replace(day=1)
            to_date = parse_date(to_date) or date.today()
        except Exception:
            return Response({"error": "Invalid date format"}, status=400)

        qs = Appointment.objects.filter(
            date__date__gte=from_date, date__date__lte=to_date
        )

        total_by_status = (
            qs.values("status").annotate(count=Count("id")).order_by("status")
        )
        total_status_dict = {item["status"]: item["count"] for item in total_by_status}

        dates = (
            qs.annotate(day=TruncDate("date")).values("day").distinct().order_by("day")
        )

        status_choices = [choice[0] for choice in Appointment.StatusChoices.choices]

        daily_counts = []
        for d in dates:
            day = d["day"]
            daily_qs = qs.filter(date__date=day)

            by_status = {
                status: daily_qs.filter(status=status).count()
                for status in status_choices
            }
            total = sum(by_status.values())

            daily_counts.append(
                {"date": str(day), "total": total, "by_status": by_status}
            )

        return Response(
            {"total_by_status": total_status_dict, "daily_counts": daily_counts}
        )
