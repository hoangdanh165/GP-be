# Generated by Django 5.1.7 on 2025-05-13 20:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0004_payment_paid'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='payment',
            name='paid',
        ),
    ]
