from django.core.management.base import BaseCommand
from service.models.service import Service
from service.models.service_embeddings import ServiceEmbeddings
from ...services.gemini_client_test import get_embedding


class Command(BaseCommand):
    help = "Generate embeddings for all services"

    def handle(self, *args, **options):
        services = Service.objects.all()
        for service in services:
            text = f"{service.name}: {service.description}"
            embedding = get_embedding(text)

            service.embedding = embedding
            service.save(update_fields=["embedding"])

            self.stdout.write(
                self.style.SUCCESS(f"Generated embedding for {service.name}")
            )
