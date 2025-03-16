from django.urls import path, include
from rest_framework import routers
from .views.user import UserViewSet

router = routers.DefaultRouter()
router.register(r'users', UserViewSet, basename='users')

app_name = "user"
urlpatterns = [
    path('api/v1/', include(router.urls)),

]
