import uuid
from django.db import models
from django.utils import timezone


class Service(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    name = models.CharField(max_length=255, unique=True, null=False, blank=False)
    description = models.TextField(null=True, blank=True)

    price = models.DecimalField(
        max_digits=10, decimal_places=2, null=False, blank=False
    )
    estimated_duration = models.DurationField(null=False, blank=False)
    create_at = models.DateTimeField(default=timezone.now)
    update_at = models.DateTimeField(auto_now=True)

    def get_date(self):
        if self.date:
            localized_time = timezone.localtime(self.date)
            return localized_time
        return None

    def get_create_at(self):
        if self.create_at:
            localized_time = timezone.localtime(self.create_at)
            return localized_time
        return None

    class Meta:
        db_table = "service"
