from ..models.service import Service
from rest_framework import serializers
from .category import CategorySerializer


class ServiceSerializer(serializers.ModelSerializer):
    category = CategorySerializer()

    class Meta:
        model = Service
        fields = [
            "id",
            "name",
            "category",
            "price",
            "discount",
            "discount_from",
            "discount_to",
            "estimated_duration",
        ]
