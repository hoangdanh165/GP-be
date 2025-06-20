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
from ..models.service import Service
from ..serializers.service import ServiceSerializer, ServiceUpdateSerializer
from ..serializers.category import CategorySerializer
from ..models.category import Category
from user.permissions import IsAdmin
from ..models.appointment_service import AppointmentService
from django.utils.timezone import now


class ServiceViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.all().order_by("id")

    permission_classes = [AllowAny]
    serializer_class = ServiceSerializer
    # pagination_class = CustomPagination

    @action(
        methods=["get"],
        url_path="all-categories",
        detail=False,
        permission_classes=[IsAuthenticated],
        renderer_classes=[renderers.JSONRenderer],
    )
    def get_all_category(self, request):
        categories = Category.objects.all().order_by("name")
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        methods=["post"],
        detail=False,
        url_path="delete-multiple",
        permission_classes=[IsAdmin],
    )
    def delete_multiple(self, request):
        service_ids = request.data.get("ids", [])

        if not service_ids:
            return Response(
                {"error": "No ID(s) found!"}, status=status.HTTP_400_BAD_REQUEST
            )

        services = Service.objects.filter(id__in=service_ids)

        if not services.exists():
            return Response(
                {"error": "Can not found service(s) with provided ID(s)!"},
                status=status.HTTP_404_NOT_FOUND,
            )

        deleted_count, _ = services.delete()

        return Response(
            {"message": f"Deleted {deleted_count} service(s) successfully!"},
            status=status.HTTP_200_OK,
        )

    @action(
        methods=["post"],
        detail=False,
        url_path="create-service",
        permission_classes=[IsAdmin],
    )
    def create_service(self, request):
        serializer = ServiceUpdateSerializer(data=request.data)

        if serializer.is_valid():
            service = serializer.save()

            return Response(
                {
                    "message": "Service created successfully!",
                    "service": ServiceSerializer(service).data,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(
        methods=["patch"],
        detail=True,
        url_path="partial-update-service",
        permission_classes=[IsAdmin],
    )
    def partial_update_service(self, request, pk=None):
        service = get_object_or_404(Service, pk=pk)

        serializer = ServiceUpdateSerializer(service, data=request.data, partial=True)

        if serializer.is_valid():
            updated_service = serializer.save()

            return Response(
                {
                    "message": "Service updated successfully!",
                    "service": ServiceSerializer(updated_service).data,
                },
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(
        methods=["get"],
        url_path="stats/category-usage-last-30-days",
        detail=False,
        permission_classes=[AllowAny],
        renderer_classes=[renderers.JSONRenderer],
    )
    def category_usage_last_30_days(self, request):
        from datetime import timedelta
        from django.db.models import Count
        from django.db.models.functions import TruncDate
        from collections import defaultdict

        today = now().date()
        start_date = today - timedelta(days=29)
        valid_statuses = ["completed", "confirmed", "processing", "pending"]

        services = (
            AppointmentService.objects.filter(
                appointment__create_at__date__gte=start_date,
                appointment__status__in=valid_statuses,
            )
            .annotate(day=TruncDate("appointment__create_at"))
            .values("day", "service__category__name")
            .annotate(count=Count("id"))
            .order_by("day")
        )

        # {(category): {day: count}}
        usage_map = defaultdict(lambda: defaultdict(int))
        categories_set = set()

        for entry in services:
            day = entry["day"]
            category = entry["service__category__name"]
            count = entry["count"]

            usage_map[category][day] += count
            categories_set.add(category)

        # Convert về format mày cần
        result = []
        for category in categories_set:
            values = []
            for i in range(30):
                day = start_date + timedelta(days=i)
                values.append(usage_map[category].get(day, 0))
            result.append({"id": category, "label": category, "data": values})

        return Response({"interval": "Last 30 days", "data": result})
