from rest_framework import viewsets, renderers
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from ..models.chatbot_history import ChatbotHistory
from ..serializers.chatbot_history import ChatbotHistorySerializer
from user.permissions import IsCustomer
from ..services.gemini import ask_gemini
from ..rag.rag import rag_response
from ..reflection.reflection import reflect_response
from ..cache.cache import get_cached_response, cache_response
from ..semantic_router.semantic_router import classify_intent


class ChatbotViewSet(viewsets.ModelViewSet):
    queryset = ChatbotHistory.objects.all().order_by("-create_at")
    serializer_class = ChatbotHistorySerializer
    permission_classes = [IsCustomer]

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

    @action(
        detail=False,
        methods=["post"],
        url_path="ask-gemini",
        permission_classes=[IsCustomer],
        renderer_classes=[renderers.JSONRenderer],
    )
    def ask_gemini(self, request):
        serializer = ChatbotHistorySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        message = serializer.validated_data["message"]

        user_message = ChatbotHistory.objects.create(
            user=request.user, message=message, is_bot=False
        )

        cached = get_cached_response(message)
        if cached:
            bot_message = ChatbotHistory.objects.create(
                user=request.user, message=cached, is_bot=True
            )
            bot_message_serializer = ChatbotHistorySerializer(bot_message)
            return Response(bot_message_serializer.data)

        intent = classify_intent(message)

        if intent in ["consult_service", "pricing"]:
            response = rag_response(message)
        else:
            response = "Sorry I don't understand your request clearly. Please tell me more information!"

        # final_response = reflect_response(message, response)
        final_response = response

        cache_response(message, final_response)

        bot_message = ChatbotHistory.objects.create(
            user=request.user, message=final_response, is_bot=True
        )
        bot_message_serializer = ChatbotHistorySerializer(bot_message)
        return Response(bot_message_serializer.data)
