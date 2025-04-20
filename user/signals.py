from django.db.models.signals import post_delete
from django.dispatch import receiver
from .models import User
from google.cloud import storage
from django.conf import settings


@receiver(post_delete, sender=User)
def delete_user_avatar_from_gcs(sender, instance, **kwargs):
    if instance.avatar:
        client = storage.Client()
        bucket = client.bucket(settings.GS_BUCKET_NAME)
        blob = bucket.blob(instance.avatar.name)
        blob.delete()
        print("DELETED AVATAR FROM GCS")
