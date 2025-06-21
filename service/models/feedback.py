from django.db import models
from user.models.user import User
from django.core.validators import MinValueValidator, MaxValueValidator
from .appointment import Appointment
import uuid


class Feedback(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    appointment = models.OneToOneField(
        Appointment, on_delete=models.CASCADE, related_name="feedback"
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="given_feedbacks"
    )
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField(null=True, blank=True)

    create_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback for {self.appointment} by {self.user}"

    class Meta:
        db_table = "feedback"
    