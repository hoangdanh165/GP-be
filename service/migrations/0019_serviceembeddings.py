# Generated by Django 5.1.7 on 2025-04-24 16:35

import django.db.models.deletion
import pgvector.django.vector
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('service', '0018_appointment_reminded_before_1d_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='ServiceEmbeddings',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('embedding', pgvector.django.vector.VectorField(dimensions=768)),
                ('service', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='embeddings', to='service.service')),
            ],
            options={
                'db_table': 'service_embeddings',
            },
        ),
    ]
