import os
from google.oauth2 import id_token
import requests
from django.shortcuts import render
from django.contrib.auth import authenticate
from django.db.models import Exists, OuterRef

from django.shortcuts import get_object_or_404
from rest_framework import viewsets, renderers
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status
from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from ..models.car import Car
from ..serializers.car import CarSerializer

from ..permissions import (
    IsAdmin,
    IsCustomer,
    IsSale,
)

CLIENT_ID = os.environ.get("CLIENT_ID")


class CarViewSet(viewsets.ModelViewSet):
    # queryset = Car.objects.all().order_by('id')

    permission_classes = [IsAuthenticated]
    serializer_class = CarSerializer
    # pagination_class = CustomPagination

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Car.objects.all()
        return Car.objects.filter(user=user)

    def perform_update(self, serializer):
        if serializer.instance != self.request.user:
            return Response(
                {"error": "You can only update your own cars!"},
                status=status.HTTP_403_FORBIDDEN,
            )
        serializer.save()

    def perform_destroy(self, instance):
        if instance != self.request.user:
            return Response(
                {"error": "You can only delete your own cars!"},
                status=status.HTTP_403_FORBIDDEN,
            )
        instance.delete()

    @action(
        detail=True,
        methods=["patch"],
        permission_classes=[IsAuthenticated],
        renderer_classes=[renderers.JSONRenderer],
    )
    def partial_update_car(self, request, pk=None):
        try:
            car = Car.objects.get(pk=pk)
        except Car.DoesNotExist:
            return Response(
                {"error": "Car not found!"}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = CarSerializer(car, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(
        methods=["post"],
        detail=False,
        url_path="delete-multiple",
        permission_classes=[IsAuthenticated],
    )
    def delete_multiple(self, request):
        car_ids = request.data.get("ids", [])
        print(car_ids)
        if not car_ids:
            return Response(
                {"error": "No ID(s) found!"}, status=status.HTTP_400_BAD_REQUEST
            )

        cars = Car.objects.filter(id__in=car_ids)

        if not cars.exists():
            return Response(
                {"error": "Can not found car(s) with provided ID(s)!"},
                status=status.HTTP_404_NOT_FOUND,
            )

        deleted_count, _ = cars.delete()

        return Response(
            {"message": f"Deleted {deleted_count} car(s) successfully!"},
            status=status.HTTP_200_OK,
        )
