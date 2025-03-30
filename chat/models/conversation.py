import uuid
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Conversation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    participants = models.ManyToManyField(User, related_name="conversations")
    last_message = models.TextField(blank=True, null=True)
    last_sender = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="last_messages"
    )
    last_message_seen = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "conversation"

    def __str__(self):
        return f"Conversation between {', '.join([user.full_name for user in self.participants.all()])}"

