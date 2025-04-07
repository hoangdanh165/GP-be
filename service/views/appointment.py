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
from ..serializers.appointment import AppointmentSerializer, AppointmentDetailSerializer


class AppointmentViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.all().order_by("id")

    permission_classes = [IsAuthenticated]
    serializer_class = AppointmentSerializer
    # pagination_class = CustomPagination

    def get(self, request):
        try:
            appointment = Appointment.objects.all()

            serializer = AppointmentDetailSerializer(appointment)

            return Response(serializer.data, status=status.HTTP_200_OK)

        except Appointment.DoesNotExist:
            return Response(
                {"detail": "Appointment not found."}, status=status.HTTP_404_NOT_FOUND
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
            serializer = AppointmentDetailSerializer(appointment)
            return Response(serializer.data)
        except Appointment.DoesNotExist:
            return Response(
                {"error": "Appointment not found."}, status=status.HTTP_404_NOT_FOUND
            )
