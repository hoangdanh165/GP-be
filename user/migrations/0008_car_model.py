# Generated by Django 5.1.7 on 2025-06-24 10:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0007_alter_car_vin'),
    ]

    operations = [
        migrations.AddField(
            model_name='car',
            name='model',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
