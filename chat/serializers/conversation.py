from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import serializers
from ..models.conversation import Conversation
User = get_user_model()

class ParticipantSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source="get_full_name")
    avatar = serializers.CharField(source="get_avatar")

    class Meta:
        model = User
        fields = ["id", "full_name", "avatar"]


class ConversationSerializer(serializers.ModelSerializer):
    participants = ParticipantSerializer(many=True)

    class Meta:
        model = Conversation
        fields = ["id", "participants", "last_message", "last_sender", "last_message_seen", "created_at", "updated_at"]