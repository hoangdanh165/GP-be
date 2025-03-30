from django.shortcuts import render
from django.db.models import Q
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
from ..models.conversation import Conversation
from ..serializers.conversation import ConversationSerializer

class ConversationViewSet(viewsets.ModelViewSet):
    # queryset = Conversation.objects.all().order_by('-create_at')
   
    permission_classes = [IsAuthenticated]
    serializer_class = ConversationSerializer
    # pagination_class = CustomPagination

    def get_queryset(self):
        user = self.request.user
        return Conversation.objects.filter(participants=user).order_by("-updated_at")
    

    @action(methods=['get'], url_path='conversations', detail=False, permission_classes=[IsAuthenticated], 
    renderer_classes=[renderers.JSONRenderer])
    def conversations(self, request):
        conversations = self.get_queryset()
        serializer = self.get_serializer(conversations, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)