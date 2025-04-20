from rest_framework import serializers
from user.models.car import Car


class CarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Car
        fields = "__all__"
        read_only_fields = ("id", "user", "create_at", "update_at")

    def create(self, validated_data):
        user = self.context["request"].user
        car = Car.objects.create(user=user, **validated_data)
        return car
