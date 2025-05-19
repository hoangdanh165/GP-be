from django.urls import path, include
from rest_framework import routers
from .views.appointment import AppointmentViewSet
from .views.service import ServiceViewSet
from .views.feedback import FeedbackViewSet

router = routers.DefaultRouter()
router.register(r"appointments", AppointmentViewSet, basename="appointments")
router.register(r"services", ServiceViewSet, basename="services")
router.register(r"feedbacks", FeedbackViewSet, basename="feedbacks")

app_name = "service"
urlpatterns = [
    path("api/v1/", include(router.urls)),
]
