# Generated by Django 5.1.7 on 2025-04-18 07:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0005_car'),
    ]

    operations = [
        migrations.AddField(
            model_name='car',
            name='brand',
            field=models.CharField(default=1, max_length=255),
            preserve_default=False,
        ),
    ]
