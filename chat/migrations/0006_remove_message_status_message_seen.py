# Generated by Django 5.1.7 on 2025-03-31 07:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0005_conversation_last_message_seen'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='message',
            name='status',
        ),
        migrations.AddField(
            model_name='message',
            name='seen',
            field=models.BooleanField(default=False),
        ),
    ]
