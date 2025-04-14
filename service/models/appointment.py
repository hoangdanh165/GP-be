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
    vehicle_ready_time = models.DateTimeField(null=True, blank=True)
    pickup_time = models.DateTimeField(null=True, blank=True)

    status = models.CharField(
        max_length=10, choices=StatusChoices.choices, default=StatusChoices.PENDING
    )

    total_price = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )

    reminded_before_1h = models.BooleanField(default=False)
    reminded_before_1d = models.BooleanField(default=False)

    create_at = models.DateTimeField(default=timezone.now)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Appointment {self.id} - {self.status}"

    def get_date(self):
        if self.date:
            localized_time = timezone.localtime(self.date)
            return localized_time
        return None

    def get_vehicle_ready_time(self):
        if self.date:
            localized_time = timezone.localtime(self.vehicle_ready_time)
            return localized_time
        return None

    def get_create_at(self):
        if self.create_at:
            localized_time = timezone.localtime(self.create_at)
            return localized_time
        return None

    def get_update_at(self):
        if self.date:
            localized_time = timezone.localtime(self.update_at)
            return localized_time
        return None

    class Meta:
        db_table = "appointment"
