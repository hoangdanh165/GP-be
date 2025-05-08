from ..models.appointment import Appointment
from rest_framework import serializers
from .appointment_service import AppointmentServiceSerializer
from user.serializers.user import UserInfoSerializer
from .appointment_service import AppointmentServiceInputSerializer
from ..models.appointment_service import AppointmentService


class AppointmentSerializer(serializers.ModelSerializer):
    date = serializers.CharField(source="get_date")
    vehicle_ready_time = serializers.CharField(source="get_vehicle_ready_time")

    class Meta:
        model = Appointment
        fields = [
            "id",
            "title",
            "date",
            "vehicle_ready_time",
            "note",
        ]


class AppointmentDetailSerializer(serializers.ModelSerializer):
    customer = UserInfoSerializer()
    appointment_services = AppointmentServiceSerializer(many=True)
    date = serializers.CharField(source="get_date")
    update_at = serializers.CharField(source="get_update_at")
    create_at = serializers.CharField(source="get_create_at")

    class Meta:
        model = Appointment
        fields = [
            "id",
            "date",
            "vehicle_ready_time",
            "status",
            "customer",
            "total_price",
            "note",
            "vehicle_information",
            "additional_customer_information",
            "appointment_services",
            "create_at",
            "update_at",
        ]


class AppointmentUpdateSerializer(serializers.ModelSerializer):
    appointment_services = AppointmentServiceInputSerializer(many=True)

    class Meta:
        model = Appointment
        fields = [
            "id",
            "date",
            "title",
            "status",
            "customer",
            "vehicle_ready_time",
            "total_price",
            "note",
            "vehicle_information",
            "additional_customer_information",
            "appointment_services",
            "create_at",
            "update_at",
        ]

    def create(self, validated_data):
        services_data = validated_data.pop("appointment_services", [])

        appointment = Appointment.objects.create(**validated_data)

        for service_data in services_data:
            AppointmentService.objects.create(
                appointment=appointment,
                service_id=service_data["service"].id,
                price=service_data["price"],
            )
        print(appointment)
        return appointment

    def update(self, instance, validated_data):
        services_data = validated_data.pop("appointment_services", [])

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        instance.appointment_services.all().delete()

        for service_data in services_data:
            print(instance, service_data["service"].id, service_data["price"])

            AppointmentService.objects.create(
                appointment=instance,
                service_id=service_data["service"].id,
                price=service_data["price"],
                completed=service_data["completed"],
            )

        return instance
