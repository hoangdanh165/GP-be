from .appointment import Appointment
from .service import Service
from django.db import models
import uuid


class AppointmentService(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    appointment = models.ForeignKey(
        Appointment, on_delete=models.CASCADE, related_name="appointment_services"
    )
    service = models.ForeignKey(
        Service, on_delete=models.CASCADE, related_name="appointment_services"
    )
    price = models.DecimalField(
        max_digits=10, decimal_places=2, null=False, blank=False
    )

    create_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "appointment_service"
