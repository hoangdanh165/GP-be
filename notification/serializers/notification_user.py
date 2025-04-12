from ..models.notification_user import NotificationUser
from ..serializers.notification import NotificationSerializer
from ..models.notification import Notification
from rest_framework import serializers


class NotificationUserSerializer(serializers.ModelSerializer):
    notification = NotificationSerializer()

    class Meta:
        model = NotificationUser
        fields = [
            "id",
            "notification",
            "user",
            "is_read",
            "create_at",
            "roles",
        ]

    def create(self, validated_data):
        notification_data = validated_data.pop("notification")

        notification = Notification.objects.create(**notification_data)

        notification_user = NotificationUser.objects.create(
            notification=notification, **validated_data
        )

        return notification_user
