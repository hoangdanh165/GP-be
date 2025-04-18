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
from user.models.user import User

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
    

    @action(methods=['post'], url_path='create', detail=False, permission_classes=[IsAuthenticated], 
            renderer_classes=[renderers.JSONRenderer])
    def create_conversation(self, request):
        participants_data = request.data.get("participants")
        print(participants_data)

        if not participants_data or not isinstance(participants_data, list):
            return Response({"error": "Participants must be a list of user IDs."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            participants = [User.objects.get(id=participant_id) for participant_id in participants_data]
        except User.DoesNotExist:
            return Response({"error": "One or more participants do not exist."}, status=status.HTTP_400_BAD_REQUEST)

        conversation = Conversation.objects.create()
        conversation.participants.set(participants)

        # Nếu bạn có serializer, bạn có thể sử dụng nó ở đây
        # serializer = self.get_serializer(conversation)
        # return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response({"message": "Conversation created successfully."}, status=status.HTTP_201_CREATED)