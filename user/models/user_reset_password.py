from django.db import models
from .user import User
import uuid

class UserResetPassword(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=255, null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    email = models.CharField(max_length=255, null=True, blank=True)
    confirmed = models.BooleanField(default=False)
    expired_time = models.DateTimeField()
    last_modified_date = models.DateTimeField(auto_now=True)
    code = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        db_table = 'user_reset_password'

