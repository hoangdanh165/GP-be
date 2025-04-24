from django.db import models
from pgvector.django import VectorField
import uuid
from .service import Service


class ServiceEmbeddings(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    service = models.ForeignKey(
        Service, on_delete=models.CASCADE, related_name="embeddings"
    )
    embedding = VectorField(dimensions=768)

    def __str__(self):
        return f"Embedding for {self.service.name}"

    class Meta:
        db_table = "service_embeddings"
