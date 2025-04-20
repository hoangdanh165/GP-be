from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views.chatbot_history import ChatbotHistoryViewSet

router = DefaultRouter()
router.register(r"chatbot-history", ChatbotHistoryViewSet, basename="chatbot-history")

urlpatterns = [
    path("", include(router.urls)),
]
