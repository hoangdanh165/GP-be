import uuid
from django.db import models
from django.contrib.auth import get_user_model
from .conversation import Conversation

User = get_user_model()


class Message(models.Model):
    MESSAGE_TYPES = [
        ("text", "Text"),
        ("image", "Image"),
        ("file", "File"),
        ("video", "Video"),
        ("audio", "Audio"),
        ("sticker", "Sticker"),
        ("reaction", "Reaction"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name="messages",
        null=True,
        blank=True,
    )

    sender = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="sent_messages"
    )
    receiver = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="received_messages",
        null=True,
        blank=True,
    )
    message = models.TextField(blank=True, null=True)
    message_type = models.CharField(
        max_length=10, choices=MESSAGE_TYPES, default="text"
    )
    seen = models.BooleanField(default=False)
    parent_message = models.ForeignKey(
        "self", on_delete=models.SET_NULL, null=True, blank=True, related_name="replies"
    )

    image = models.ImageField(upload_to="media/message_images/", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        conversation = (
            Conversation.objects.filter(participants=self.sender)
            .filter(participants=self.receiver)
            .first()
        )

        if not conversation:
            conversation = Conversation.objects.create()
            conversation.participants.add(self.sender, self.receiver)

        conversation.last_message = self.message
        conversation.save()

    def __str__(self):
        return f"Message from {self.sender} to {self.receiver or 'Group'} ({self.message_type})"

    class Meta:
        db_table = "message"
        indexes = [
            models.Index(fields=["created_at"]),
            models.Index(fields=["sender", "receiver", "created_at"]),
        ]
