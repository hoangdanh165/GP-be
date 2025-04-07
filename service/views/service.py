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
from ..serializers.service import ServiceSerializer


class ServiceViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.all().order_by("id")

    permission_classes = [IsAuthenticated]
    serializer_class = ServiceSerializer
    # pagination_class = CustomPagination

    @action(
        methods=["post"],
        url_path="",
        detail=False,
        permission_classes=[IsAuthenticated],
        renderer_classes=[renderers.JSONRenderer],
    )
    def something(self, request):
        pass
