from rest_framework import serializers
from user.models.user_reset_password import UserResetPassword

class UserResetPasswordSerializer(serializers.Serializer):
    class Meta:
        model = UserResetPassword
        fields = '__all__'
