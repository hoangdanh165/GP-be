from django.urls import path, include
from rest_framework import routers
from .views.message import MessageViewSet

router = routers.DefaultRouter()
router.register(r'chat', MessageViewSet, basename='chat')

app_name = "chat"
urlpatterns = [
    path('api/v1/', include(router.urls)),

]
