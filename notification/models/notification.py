from django.db import models
import uuid


class Notification(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    message = models.TextField()
    params = models.JSONField(null=True, blank=True)
    create_url = models.TextField(null=True, blank=True)
    extra_data = models.JSONField(null=True, blank=True)

    class Meta:
        db_table = "notification"
