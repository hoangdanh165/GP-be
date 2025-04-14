from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils import timezone
from django.utils.timezone import now, timedelta

from datetime import datetime
from django.conf import settings
import jwt
import requests


def send_appointment_reminder_email(user, appointment_time, services, template):
    subject = (
        f"🚗 [Prestige Auto Garage] Service Appointment Reminder - {appointment_time}"
    )

    html_content = render_to_string(
        template,
        {
            "customer_name": user.get_full_name() or user.username,
            "appointment_time": appointment_time,
            "services": services,
        },
    )
    text_content = strip_tags(html_content)
    text_content += f"\n\nConfirm your appointment at: "

    email = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user.email],
    )
    email.attach_alternative(html_content, "text/html")
    email.send()
