from django.shortcuts import render

import os
from google.oauth2 import id_token
import requests
from django.shortcuts import render
from django.contrib.auth import authenticate
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, renderers
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import action
from rest_framework import status
from rest_framework_simplejwt.tokens import BlacklistedToken, RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from base.utils.custom_pagination import CustomPagination
from ..models.message import Message
from ..serializers.message import MessageSerializer

class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all().order_by('id')
   
    permission_classes = [IsAuthenticated]
    serializer_class = MessageSerializer
    # pagination_class = CustomPagination

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)