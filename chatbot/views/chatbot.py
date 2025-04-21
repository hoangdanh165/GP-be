from rest_framework import viewsets, renderers
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from ..models.chatbot_history import ChatbotHistory
from ..serializers.chatbot_history import ChatbotHistorySerializer
from user.permissions import IsCustomer
from ..services.gemini import ask_gemini


class ChatbotViewSet(viewsets.ModelViewSet):
    queryset = ChatbotHistory.objects.all().order_by("-create_at")
    serializer_class = ChatbotHistorySerializer
    permission_classes = [IsCustomer]

    @action(
        detail=False,
        methods=["get"],
        url_path="recent",
        permission_classes=[IsCustomer],
        renderer_classes=renderers.JSONRenderer,
    )
    def recent(self, request):
        user = request.user
        recent_histories = ChatbotHistory.objects.filter(user=user).order_by(
            "-create_at"
        )[:5]
        serializer = self.get_serializer(recent_histories, many=True)
        return Response(serializer.data)

    @action(
        detail=False,
        methods=["get"],
        url_path="history",
        permission_classes=[IsCustomer],
        renderer_classes=[renderers.JSONRenderer],
    )
    def history(self, request):
        user = request.user
        recent_histories = ChatbotHistory.objects.filter(user=user).order_by(
            "create_at"
        )
        serializer = self.get_serializer(recent_histories, many=True)
        return Response(serializer.data)

    @action(
        detail=False,
        methods=["post"],
        url_path="ask",
        permission_classes=[IsCustomer],
        renderer_classes=[renderers.JSONRenderer],
    )
    def ask_chatbot(self, request):
        serializer = ChatbotHistorySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        message = serializer.validated_data["message"]

        user_message = ChatbotHistory.objects.create(
            id=request.data.get("id"),
            user=request.user,
            message=message,
            is_bot=False,
        )

        response = ask_gemini(message, request.user.id)

        bot_response = ChatbotHistory.objects.create(
            user=request.user,
            message=response,
            is_bot=True,
        )

        return Response(
            {
                "id": str(bot_response.id),
                "message": bot_response.message,
                "user": bot_response.user.id,
                "is_bot": bot_response.is_bot,
                "create_at": bot_response.create_at,
            },
            status=status.HTTP_200_OK,
        )
