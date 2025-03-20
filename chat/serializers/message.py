from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import serializers
from ..models.message import Message

class MessageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Message
        fields = '__all__'
    