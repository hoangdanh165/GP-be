from rest_framework import serializers
from ..models.chatbot_history import ChatbotHistory


class ChatbotHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatbotHistory
        fields = "__all__"
