from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import NotificationUserViewSet

router = DefaultRouter()
router.register(r'notifications', NotificationUserViewSet)

urlpatterns = [
    path('api/v1/', include(router.urls)),
]
