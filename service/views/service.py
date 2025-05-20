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
