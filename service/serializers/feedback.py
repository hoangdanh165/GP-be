from ..models.feedback import Feedback
from rest_framework import serializers


class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = "__all__"


class FeedbackDetailSerializer(serializers.ModelSerializer):
    user_full_name = serializers.SerializerMethodField()

    class Meta:
        model = Feedback
        fields = [
            "id",
            "comment",
            "rating",
            "appointment",
            "user_full_name",
            "create_at",
        ]

    def get_user_full_name(self, obj):
        return obj.user.get_full_name() if obj.user else None
