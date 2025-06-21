import os
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, renderers
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status
from django.conf import settings
from django.utils import timezone
from base.utils.custom_pagination import CustomPagination, CustomPaginationFeedback
from ..models.feedback import Feedback
from ..serializers.feedback import FeedbackSerializer, FeedbackDetailSerializer
from ..models.appointment import Appointment
from user.permissions import IsAdminOrSale
from django.utils.dateparse import parse_date
from functools import reduce
import operator
from django.db.models import Q
from django.db.models import Avg, Count


class FeedbackViewSet(viewsets.ModelViewSet):
    queryset = Feedback.objects.all().order_by("-create_at")

    permission_classes = [IsAuthenticated]
    serializer_class = FeedbackSerializer
    # pagination_class = CustomPagination

    @action(
        methods=["post"],
        url_path="create-for-appointment",
        detail=False,
        permission_classes=[IsAuthenticated],
        renderer_classes=[renderers.JSONRenderer],
    )
    def create_for_appointment(self, request):
        appointment_id = request.data.get("appointment_id")
        comment = request.data.get("comment")
        rating = request.data.get("rating")

        if not appointment_id or rating is None:
            return Response(
                {"detail": "Missing 'appointment_id' or 'rating'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            appointment = Appointment.objects.get(id=appointment_id)
        except Appointment.DoesNotExist:
            return Response(
                {"detail": "Appointment not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if Feedback.objects.filter(appointment=appointment).exists():
            return Response(
                {"detail": "Feedback already exists for this appointment."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        feedback = Feedback.objects.create(
            appointment=appointment,
            rating=rating,
            comment=comment,
            user=request.user,
        )

        appointment.feedback_sent = True
        appointment.save(update_fields=["feedback_sent"])

        serializer = self.get_serializer(feedback)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(
        methods=["get"],
        url_path="get-by-appointment",
        detail=False,
        permission_classes=[IsAuthenticated],
        renderer_classes=[renderers.JSONRenderer],
    )
    def get_by_appointment(self, request):
        appointment_id = request.query_params.get("appointment_id")
        if not appointment_id:
            return Response(
                {"detail": "Missing 'appointment_id' query parameter."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        feedback = Feedback.objects.filter(appointment__id=appointment_id).first()
        if not feedback:
            return Response(
                {"detail": "No feedback found for this appointment."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = self.get_serializer(feedback)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        methods=["get"],
        url_path="all",
        detail=False,
        permission_classes=[IsAdminOrSale],
        renderer_classes=[renderers.JSONRenderer],
    )
    def all(self, request):
        try:
            feedbacks = Feedback.objects.all().order_by("-create_at")

            search = request.query_params.get("search")
            rating_filter = request.query_params.get("rating")
            start_date_str = request.query_params.get("start_date")
            end_date_str = request.query_params.get("end_date")

            search_fields = [
                "user__full_name",
            ]

            if search:
                query = reduce(
                    operator.or_,
                    [Q(**{f"{field}__icontains": search}) for field in search_fields],
                )
                feedbacks = feedbacks.filter(query)

            if rating_filter:
                feedbacks = feedbacks.filter(rating=rating_filter)

            if start_date_str:
                start_date = parse_date(start_date_str)
                if start_date:
                    feedbacks = feedbacks.filter(create_at__date__gte=start_date)

            if end_date_str:
                end_date = parse_date(end_date_str)
                if end_date:
                    feedbacks = feedbacks.filter(create_at__date__lte=end_date)

            paginator = CustomPaginationFeedback()
            paginated_feedbacks = paginator.paginate_queryset(feedbacks, request)

            serializer = FeedbackDetailSerializer(paginated_feedbacks, many=True)

            return paginator.get_paginated_response({"data": serializer.data})

        except Exception as e:
            return Response(
                {"error": f"Something went wrong: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(
        methods=["get"],
        url_path="stats/average-rating-all-time",
        detail=False,
        permission_classes=[IsAuthenticated],
        renderer_classes=[renderers.JSONRenderer],
    )
    def garage_rating(self, request):

        stats = Feedback.objects.aggregate(
            average_rating=Avg("rating"), total_feedback=Count("id")
        )

        return Response(
            {
                "title": "Garage's rating",
                "value": round(stats["average_rating"] or 0, 1),
                "total": stats["total_feedback"] or 0,
            }
        )
