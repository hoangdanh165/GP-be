from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views.chatbot import ChatbotViewSet

router = DefaultRouter()
router.register(r"chatbot", ChatbotViewSet, basename="chatbot")

app_name = "chatbot"
urlpatterns = [
    path("api/v1/", include(router.urls)),
]
