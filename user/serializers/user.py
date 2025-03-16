from rest_framework import serializers
from django.contrib.auth import get_user_model
from ..serializers.role import RoleSerializer
from django.core.mail import send_mail
from django.urls import reverse
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.core.exceptions import ValidationError

from ..models.role import Role

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    role = RoleSerializer(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'password', 'phone', 'status', 'role', 'email_verified']
        extra_kwargs = {
            'password': {'write_only': True}  
        }



    def validate_password(self, value):
        if len(value) < 8:
            raise ValidationError("Mật khẩu phải có độ dài tối thiểu là 8 ký tự.")
        return value

    
    def validate(self, attrs):
        email = attrs.get("email", None)
        password = attrs.get("password", None)
        
        if email is None:
            raise ValidationError({"detail": "email is missing"})
        
        if password is None:
            raise ValidationError({"detail": "password is missing"})
        
        return attrs
        

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])  
        validated_data['status'] = 1
        validated_data['email_verified'] = False  
        user = User.objects.create(**validated_data)
        return user


class UserAccountSerializer(serializers.ModelSerializer):
    role = RoleSerializer()
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'status', 'avatar_url', 'email_verified', 'role', 'password']
        read_only_fields = ['id', 'avatar_url']

    def get_status(self, obj):
        status_dict = {
            1: 'ACTIVE',
            2: 'BLOCKED',
            3: 'INVITED',
        }
        return status_dict.get(obj.status, 'Unknown') 
    
    def update(self, instance, validated_data):
        role_data = validated_data.get('role')
        if role_data and 'name' in role_data:
            try:
                role_instance = Role.objects.get(name=role_data['name'])
                instance.role = role_instance
            except Role.DoesNotExist:
                raise serializers.ValidationError(f"Role '{role_data['name']}' does not exist.")
        else:
            instance.role = instance.role

        instance.status = validated_data.get('status', instance.status)
        instance.email_verified = validated_data.get('email_verified', instance.email_verified)
        instance.save()
                
        return instance 
    
    def create(self, validated_data):
        role_data = validated_data.pop('role', None)
        if role_data and 'name' in role_data:
            try:
                role_instance = Role.objects.get(name=role_data['name'])
            except Role.DoesNotExist:
                raise serializers.ValidationError(f"Role '{role_data['name']}' does not exist.")
        else:
            role_instance = None
        
        password = validated_data.pop('password', None)

        user = User.objects.create(
            role=role_instance,
            **validated_data
        )

        if password:
            user.set_password(password)
            user.save()

        return user

    

    
class UserInfoSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['id', 'email', 'phone', 'status', 
                  'email_verified', 'avatar_url']
    

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['phone', 'avatar_url', 'email']
