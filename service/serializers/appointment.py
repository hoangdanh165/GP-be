from ..models.appointment import Appointment
from rest_framework import serializers
from .appointment_service import AppointmentServiceSerializer
from user.serializers.user import UserInfoSerializer


class AppointmentSerializer(serializers.ModelSerializer):
    date = serializers.CharField(source="get_date")
    estimated_end_time = serializers.CharField(source="get_estimated_end_time")

    class Meta:
        model = Appointment
        fields = [
            "id",
            "title",
            "date",
            "estimated_end_time",
            "note",
        ]


class AppointmentDetailSerializer(serializers.ModelSerializer):
    customer = UserInfoSerializer()
    appointment_services = AppointmentServiceSerializer(many=True)
    date = serializers.CharField(source="get_date")

    class Meta:
        model = Appointment
        fields = [
            "id",
            "date",
            "estimated_end_time",
            "status",
            "customer",
            "total_price",
            "note",
            "vehicle_information",
            "additional_customer_information",
            "appointment_services",
        ]
