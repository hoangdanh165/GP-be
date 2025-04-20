from django.db import models
import uuid
from .user import User


class Car(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="cars")

    name = models.CharField(max_length=255)
    brand = models.CharField(max_length=255)
    color = models.CharField(max_length=50, blank=True, null=True)
    year = models.PositiveIntegerField()
    engine_type = models.CharField(max_length=255)
    current_odometer = models.PositiveIntegerField(
        help_text="Distance traveled in kilometers"
    )
    license_plate = models.CharField(max_length=20, blank=True, null=True)
    registration_province = models.CharField(max_length=255)
    vin = models.CharField(
        max_length=100, blank=True, null=True
    )  # Vehicle Identification Number

    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.year})"

    class Meta:
        db_table = "car"
        ordering = ["-create_at"]
