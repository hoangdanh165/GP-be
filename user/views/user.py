
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
from ..models import UserResetPassword 
from django.utils import timezone
from ..serializers import UserSerializer, UserResetPasswordSerializer
from ..serializers.user import UserInfoSerializer
from ..serializers.user import UserAccountSerializer
from ..models import User, UserResetPassword
from base.utils.custom_pagination import CustomPagination
from ..services.user import (
    verify_token, 
    send_verification_email, 
    send_password_reset_email,
    send_sms,
    verify_sms_code,
)
from ..permissions import (
    IsAdmin, 
    IsCustomer, 
    IsSale,
)

CLIENT_ID = os.environ.get('CLIENT_ID')

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('id')
   
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer
    # pagination_class = CustomPagination

    def get_serializer_class(self):
        if self.action == 'list':
            return UserSerializer  
        elif self.action == 'retrieve':
            return UserSerializer  
        elif self.action == 'create':
            return UserAccountSerializer  
        elif self.action in ['update', 'partial_update']:
            return UserAccountSerializer  
        return UserSerializer  


    def patch(self, request, pk, format=None):
        try:
            user = User.objects.get(pk=pk)  
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = UserAccountSerializer(user, data=request.data, partial=True)  

        if serializer.is_valid():
            serializer.save()  
            return Response(serializer.data)  
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)  

    @action(methods=['post'], url_path='sign-up', detail=False, permission_classes=[AllowAny], 
            renderer_classes=[renderers.JSONRenderer])
    def sign_up(self, request):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()
            send_verification_email(user)

            return Response({'detail': 'Account created successfully, please check your email!'}, 
                            status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

    @action(methods=['post'], url_path='send-verification-email', detail=False, permission_classes=[IsAuthenticated], 
            renderer_classes=[renderers.JSONRenderer])
    def send_verification_email(self, request):
        email = request.data.get('email')
        user = request.user
        
        if not email:
            return Response({'status': 'Please provide your email!'}, 
                        status=status.HTTP_400_BAD_REQUEST)
        
        if not user:
            return Response({'status': 'Unauthorized!'}, 
                        status=status.HTTP_401_UNAUTHORIZED)

        send_verification_email(user)

        return Response({'status': 'Verification email sent, please check your email!'}, 
                        status=status.HTTP_200_OK)


    @action(methods=['get'], url_path='verify-email', detail=False, permission_classes=[AllowAny],
            renderer_classes=[renderers.JSONRenderer])
    def verify_email(self, request, *args, **kwargs):
        token = request.query_params.get('token')
        user_id = verify_token(token)
        if user_id is None:
            return Response({'status': 'Invalid or expired token'}, status=status.HTTP_400_BAD_REQUEST)

        user = get_object_or_404(User, id=user_id)
        if user.email_verified == True:
            return render(request, 'user/email/email_verified.html', {'frontend_host': settings.FE_HOST})
        
        user.email_verified = True
        user.save()


        return render(request, 'user/email/email_verification_success.html', {'frontend_host': settings.FE_HOST})
    

    @action(methods=['post'], url_path='forgot-password', detail=False, permission_classes=[AllowAny],
            renderer_classes=[renderers.JSONRenderer])
    def forgot_password(self, request, *args, **kwargs):     
        email = request.data.get('email')
        if not email:
            return Response({'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'User with this email does not exist!'}, status=status.HTTP_404_NOT_FOUND)

        send_password_reset_email(user)
        return Response({'status': 'Password reset link has been sent to your email'}, status=status.HTTP_200_OK)
    

    @action(methods=['get'], url_path='handle-forgot-password', detail=False, permission_classes=[AllowAny],
            renderer_classes=[renderers.JSONRenderer])
    def handle_forgot_password(self, request, *args, **kwargs):
        token = request.query_params.get('token')
        user_id = verify_token(token)
        if user_id is None:
            return Response({'error': 'Invalid or expired token!'}, status=status.HTTP_400_BAD_REQUEST)
        
        if not UserResetPassword.objects.filter(user_id=user_id, token=token).exists():
            UserResetPassword.objects.create(
                user = User.objects.get(id=user_id),
                token = token,
                expired_time=timezone.now() + timezone.timedelta(hours=1),
            )
        
        if UserResetPassword.objects.filter(user_id=user_id, token=token, confirmed=True).exists():
            return render(request, 'user/reset_password/reset-password-expired.html', { 'frontend_host': settings.FE_HOST })

        return render(request, 'user/reset_password/reset-password-form.html', {'token': token, 'frontend_host': settings.FE_HOST})

    
    @action(methods=['post'], url_path='reset-password', detail=False, permission_classes=[AllowAny],
            renderer_classes=[renderers.JSONRenderer])
    def reset_password(self, request, *args, **kwargs):
        token = request.query_params.get('token')

        user_id = verify_token(token)

        user = User.objects.get(id=user_id)
        
        if not user:
            return Response({'error': 'No token provided!'}, status=status.HTTP_400_BAD_REQUEST)
        
        new_password = request.data.get('password')

        
        if not token or not new_password:
            return Response({'error': 'Token and new password are required!'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            reset_entry = UserResetPassword.objects.filter(token=token).first()

            if not reset_entry: 
                return Response({'error': 'Not found!'}, status=status.HTTP_400_BAD_REQUEST)
            if reset_entry.expired_time < timezone.now():
                return Response({'error': 'Token has expired!'}, status=status.HTTP_400_BAD_REQUEST)
            if reset_entry.confirmed == True: 
                return Response({'error': 'This link is expired!'})
            
            user = reset_entry.user

            user.password = make_password(new_password) 
            user.save()
            reset_entry.confirmed = True
            reset_entry.save()
            return Response({'message': 'Password has been reset successfully!'}, status=status.HTTP_200_OK)
        
        
        except UserResetPassword.DoesNotExist:
            return Response({'error': 'Invalid token!'}, status=status.HTTP_400_BAD_REQUEST)


    @action(methods=['post'], url_path='change-password', detail=False, permission_classes=[IsAuthenticated],
            renderer_classes=[renderers.JSONRenderer])
    def change_password(self, request, *args, **kwargs):
        current_password = request.data.get('current_password')
        new_password = request.data.get('new_password')
        user = request.user
        
        if not user.check_password(current_password):
            return Response({'error': 'Current password is not correct!'}, status=status.HTTP_400_BAD_REQUEST)
        
        if len(new_password) < 8:
            return Response({'error': 'Password must have atleast 8 characters!'}, status=status.HTTP_400_BAD_REQUEST)
        
        user.set_password(new_password)
        user.save()
        return Response({'message': 'Your password has been changed!'}, status=status.HTTP_200_OK)


    @action(methods=['get'], url_path='info', detail=False, permission_classes=[IsAuthenticated],
            renderer_classes=[renderers.JSONRenderer])
    def info(self, request):
        user = request.user  
        serializer = UserInfoSerializer(user, context={'request': request})  

        return Response(serializer.data)
        

    @action(methods=['get'], url_path='identity', detail=False, permission_classes=[IsAuthenticated], 
            renderer_classes=[renderers.JSONRenderer])
    def identity(self, request):
        user = request.user  
        serializer = UserSerializer(user)  

        return Response(serializer.data)


    @action(methods=['post'], url_path='log-out', detail=False, permission_classes=[IsAuthenticated], 
        renderer_classes=[renderers.JSONRenderer])
    def log_out(self, request):
        try:
            refresh_token = request.COOKIES.get('refreshToken')
            
            token = RefreshToken(refresh_token)
            
            token.blacklist()
            response = Response(status=204)
            response.delete_cookie('refreshToken', path='/')  

            return response
        except Exception as e:
            return Response({"error": str(e)}, status=400)


    @action(methods=['post'], url_path='sign-in', detail=False, permission_classes=[AllowAny], 
            renderer_classes=[renderers.JSONRenderer])
    def sign_in(self, request):
        email = request.data.get("email")
        password = request.data.get("password")
        
        
        try:
            check_user = User.objects.filter(email=email).first()

            if check_user:
                if not check_user.password:
                    return Response({"error": "This account was registered using Google. Please sign in with Google."}, status=status.HTTP_400_BAD_REQUEST)
                
            user = authenticate(request, username=email, password=password)
            if user is not None:
                refresh = RefreshToken.for_user(user)
                access_token = str(refresh.access_token)
                refresh_token = str(refresh)
                avatar = user.avatar
                full_name = user.full_name

                if avatar:
                    avatar = avatar.url
                else:
                    avatar = None

                response = Response({
                    "accessToken": access_token,
                    "refreshToken": refresh_token,
                    "role": user.role.name,
                    "status": user.status,
                    "avatar": avatar,
                    "fullName": full_name,
                }, status=status.HTTP_200_OK)

                response.set_cookie(
                    key='refreshToken',
                    value=refresh_token,
                    httponly=True,  
                    secure=True, # True if Production mode is on
                    samesite='None', 
                    max_age=24*60*60, 
                )
                return response
            else:
                return Response({"error": "Invalid username or password!"}, status=status.HTTP_401_UNAUTHORIZED)
            
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    @action(methods=['post'], url_path='sign-in-with-google', detail=False, permission_classes=[AllowAny], renderer_classes=[renderers.JSONRenderer])
    def sign_in_with_google(self, request): 
        access_token  = request.data.get("token")

        if not access_token:
            return Response({"error": "Missing access_token"}, status=400)
        
        google_user_info_url = "https://www.googleapis.com/oauth2/v3/userinfo"

        response = requests.get(google_user_info_url, headers={"Authorization": f"Bearer {access_token}"})
        
        if response.status_code != 200:
            return Response({"error": "Invalid access token"}, status=400)
        
        user_info = response.json()
        
        email = user_info.get("email")
        email_verified = user_info.get("email_verified")
        full_name = user_info.get("name")
        avatar = user_info.get("picture")
        google_id = user_info.get("sub")
        
        user = User.objects.filter(google_id=google_id).first()

        if user:
            if user.email != email:
                user.email = email
                user.save()
        else:
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    "full_name": full_name,
                    "email_verified": email_verified,
                    "avatar": avatar,
                    "google_id": google_id
                }
            )

            if not created:
                user.full_name = full_name
                user.avatar = avatar
                user.email_verified = email_verified
                user.google_id = google_id
                user.save()

        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)
        
        response = Response({
            "accessToken": access_token,
            "refreshToken": refresh_token,
            "role": user.role.name,
            "status": user.status,
            "avatar": avatar,
            "fullName": full_name,
        }, status=status.HTTP_200_OK)

        response.set_cookie(
            key='refreshToken',
            value=refresh_token,
            httponly=True,  
            secure=True,
            samesite='None', 
            max_age=24*60*60, 
        )

        return response
        
        


    @action(methods=['post'], url_path='refresh', detail=False, permission_classes=[AllowAny], 
            renderer_classes=[renderers.JSONRenderer])
    def refresh(self, request):
        refresh_token = request.COOKIES.get('refreshToken')

        if not refresh_token:
            return Response({"detail": "Refresh token not found"}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            token = RefreshToken(refresh_token)
            new_access_token = str(token.access_token)

            user_id = token['user_id']  
            user = User.objects.get(id=user_id)

            avatar = user.avatar
            full_name = user.full_name

            
            if avatar:
                avatar = avatar.url
            elif user.avatar_url:
                avatar = user.avatar_url
            else:
                avatar = None
            
            return Response({
                "accessToken": new_access_token,
                "role": user.role.name,
                "avatar": avatar,
                "status": user.status,
                "fullName": full_name,
                "email": user.email,
            }, status=status.HTTP_200_OK)

        except TokenError:
            return Response({"detail": "Invalid refresh token"}, status=status.HTTP_401_UNAUTHORIZED)
        

    @action(methods=['post'], detail=False, url_path='delete-multiple', permission_classes=[IsAdmin])
    def delete_multiple(self, request):
        user_ids = request.data.get('ids', [])
        print(user_ids)
        if not user_ids:
            return Response({'error': 'No ID(s) found!'}, status=status.HTTP_400_BAD_REQUEST)
        
        users = User.objects.filter(id__in=user_ids)
        
        if not users.exists():
            return Response({'error': 'Can not found user(s) with provided ID(s)!'}, status=status.HTTP_404_NOT_FOUND)
        
        deleted_count, _ = users.delete()
        
        return Response({'message': f'Deleted {deleted_count} user(s) successfully!'}, status=status.HTTP_200_OK)