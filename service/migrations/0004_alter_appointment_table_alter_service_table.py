# Generated by Django 5.1.7 on 2025-04-07 12:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('service', '0003_alter_appointment_total_price'),
    ]

    operations = [
        migrations.AlterModelTable(
            name='appointment',
            table='appointment',
        ),
        migrations.AlterModelTable(
            name='service',
            table='service',
        ),
    ]
