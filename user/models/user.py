from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from .role import Role
from user.managers import UserManager
from django.contrib.auth.models import PermissionsMixin
import uuid
from django.conf import settings
from django.utils import timezone


class User(AbstractBaseUser, PermissionsMixin):
    class Status(models.IntegerChoices):
        ACTIVE = 1, "Active"
        BANNED = 0, "Banned"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    google_id = models.CharField(max_length=50, unique=True, null=True, blank=True)

    full_name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, unique=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)

    password = models.CharField(max_length=255, null=True, blank=True)
    role = models.ForeignKey(
        Role, on_delete=models.SET_NULL, null=True, blank=True, default=1
    )
    status = models.IntegerField(choices=Status.choices, default=Status.ACTIVE)
    email_verified = models.BooleanField(default=False)

    create_at = models.DateTimeField(auto_now_add=True)
    avatar = models.ImageField(upload_to="media/avatars/", blank=True, null=True)
    avatar_url = models.CharField(max_length=2048, blank=True, null=True)

    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

    class Meta:
        db_table = "user"

    def get_phone(self):
        if self.phone:
            if self.phone.startswith("+84"):
                return "0" + self.phone[3:]
            return self.phone
        return None

    def get_create_at(self):
        if self.create_at:
            localized_time = timezone.localtime(self.create_at)
            return localized_time
        return None

    def get_full_name(self):
        return self.full_name

    def get_role(self):
        return self.role.name

    def get_status(self):
        return self.get_status_display()

    def get_avatar(self):
        if self.google_id:
            return self.avatar_url
        else:
            if self.avatar:
                return self.avatar.url
            return settings.MEDIA_URL + "default-avatar.jpg"
