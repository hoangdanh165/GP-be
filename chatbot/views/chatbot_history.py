from rest_framework import viewsets, renderers
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from ..models.chatbot_history import ChatbotHistory
from ..serializers.chatbot_history import ChatbotHistorySerializer
from user.permissions import IsCustomer


class ChatbotHistoryViewSet(viewsets.ModelViewSet):
    queryset = ChatbotHistory.objects.all().order_by("-created_at")
    serializer_class = ChatbotHistorySerializer
    permission_classes = [IsCustomer]

    @action(
        detail=False,
        methods=["get"],
        path="recent",
        permission_classes=[IsCustomer],
        renderer_classes=renderers.JSONRenderer,
    )
    def recent(self, request):
        user = request.user
        recent_histories = ChatbotHistory.objects.filter(user=user).order_by(
            "-created_at"
        )[:5]
        serializer = self.get_serializer(recent_histories, many=True)
        return Response(serializer.data)

    @action(
        detail=False,
        methods=["get"],
        path="all",
        permission_classes=[IsCustomer],
        renderer_classes=renderers.JSONRenderer,
    )
    def get_all(self, request):
        user = request.user
        recent_histories = ChatbotHistory.objects.filter(user=user).order_by(
            "-created_at"
        )
        serializer = self.get_serializer(recent_histories, many=True)
        return Response(serializer.data)
