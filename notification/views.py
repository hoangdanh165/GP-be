from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models.notification_user import NotificationUser
from .models.notification import Notification
from .serializers.notification_user import NotificationUserSerializer
from base.utils.custom_pagination import CustomPaginationNotification
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from rest_framework import renderers


class NotificationUserViewSet(viewsets.ModelViewSet):
    queryset = NotificationUser.objects.all().order_by("-create_at")
    serializer_class = NotificationUserSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPaginationNotification

    def list(self, request, *args, **kwargs):
        user = request.user
        role = user.role.name

        user_notifications = self.queryset.filter(user=user)

        role_notifications = self.queryset.filter(roles__icontains=role)

        notifications = (user_notifications | role_notifications).distinct()

        page = self.paginate_queryset(notifications)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        return Response(
            {"detail": "No notifications for this user found."},
            status=status.HTTP_404_NOT_FOUND,
        )

    @action(
        methods=["get"],
        url_path="get-by-role",
        detail=False,
        permission_classes=[IsAuthenticated],
        renderer_classes=[renderers.JSONRenderer],
    )
    def get_by_role(self, request, *args, **kwargs):
        role = request.user.role.name
        notifications = self.queryset.filter(roles__icontains=role)
        page = self.paginate_queryset(notifications)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        return Response(
            {"detail": "No notifications for those roles found."},
            status=status.HTTP_404_NOT_FOUND,
        )
