import uuid
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Message(models.Model):
    MESSAGE_TYPES = [
        ('text', 'Text'),
        ('image', 'Image'),
        ('file', 'File'),
        ('video', 'Video'),
        ('audio', 'Audio'),
        ('sticker', 'Sticker'),
        ('reaction', 'Reaction'),
    ]

    STATUS_TYPES = [
        ('sent', 'Sent'),
        ('received', 'Received'),
        ('seen', 'Seen'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_messages")
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="received_messages", null=True, blank=True)
    message = models.TextField(blank=True, null=True)
    message_type = models.CharField(max_length=10, choices=MESSAGE_TYPES, default='text')
    status = models.CharField(max_length=10, choices=STATUS_TYPES, default='sent')
    parent_message = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name="replies")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Message from {self.sender} to {self.receiver or 'Group'} ({self.message_type})"
