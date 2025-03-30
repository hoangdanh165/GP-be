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
from ..serializers.message import MessageSerializer
from ..models.conversation import Conversation  



class MessageViewSet(viewsets.ModelViewSet):
    # queryset = Message.objects.all().order_by('-create_at')
   
    permission_classes = [IsAuthenticated]
    serializer_class = MessageSerializer
    # pagination_class = CustomPagination

    def get_queryset(self):
        user = self.request.user
        return Message.objects.filter(Q(sender=user) | Q(receiver=user)).order_by("created_at")
    

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)

    @action(methods=['get'], url_path='chat-with', detail=False, permission_classes=[IsAuthenticated], 
    renderer_classes=[renderers.JSONRenderer])
    def chat_with(self, request):
        other_user_id = request.query_params.get("user_id")
        if not other_user_id:
            return Response({"error": "user_id is required"}, status=400)

        messages = Message.objects.filter(
            Q(sender=request.user, receiver_id=other_user_id) |
            Q(sender_id=other_user_id, receiver=request.user)
        ).order_by("created_at")

        serializer = self.get_serializer(messages, many=True)
        return Response(serializer.data)
    
    @action(methods=['get'], url_path='by-conversation/(?P<conversation_id>[^/.]+)', detail=False, permission_classes=[IsAuthenticated])
    def get_messages_by_conversation(self, request, conversation_id):
        """ Lấy tất cả tin nhắn theo `conversation_id` (hỗ trợ phân trang). """
        conversation = get_object_or_404(Conversation, id=conversation_id)

        if request.user not in conversation.participants.all():
            return Response({"error": "Bạn không có quyền truy cập vào cuộc trò chuyện này!"}, status=403)

        messages = Message.objects.filter(conversation=conversation).order_by("created_at")

        page = self.paginate_queryset(messages)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(messages, many=True)
        return Response(serializer.data)