import uuid
from django.db import models
from django.utils import timezone
from user.models.user import User


class Appointment(models.Model):
    class StatusChoices(models.TextChoices):
        PENDING = "pending", "Pending"
        CONFIRMED = "confirmed", "Confirmed"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.TextField(null=True, blank=True)
    customer = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="appointments"
    )
    additional_customer_information = models.JSONField(null=True, blank=True)
    vehicle_information = models.JSONField(null=True, blank=True)

    note = models.TextField(null=True, blank=True)
    date = models.DateTimeField()
    estimated_end_time = models.DateTimeField(null=True, blank=True)

    status = models.CharField(
        max_length=10, choices=StatusChoices.choices, default=StatusChoices.PENDING
    )

    total_price = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )

    create_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Appointment {self.id} - {self.status}"

    def get_date(self):
        if self.date:
            localized_time = timezone.localtime(self.date)
            return localized_time
        return None

    def get_estimated_end_time(self):
        if self.date:
            localized_time = timezone.localtime(self.estimated_end_time)
            return localized_time
        return None

    def get_create_at(self):
        if self.create_at:
            localized_time = timezone.localtime(self.create_at)
            return localized_time
        return None

    class Meta:
        db_table = "appointment"
