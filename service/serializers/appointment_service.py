from ..models.appointment import Appointment
from rest_framework import serializers
from ..models.appointment_service import AppointmentService
from ..serializers.service import ServiceSerializer


class AppointmentServiceSerializer(serializers.ModelSerializer):
    service = ServiceSerializer()

    class Meta:
        model = AppointmentService
        fields = ["id", "service", "price"]
