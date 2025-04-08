from django.urls import path, include
from rest_framework import routers
from .views.appointment import AppointmentViewSet
from .views.service import ServiceViewSet

router = routers.DefaultRouter()
router.register(r"appointments", AppointmentViewSet, basename="appointments")
router.register(r"services", ServiceViewSet, basename="services")

app_name = "service"
urlpatterns = [
    path("api/v1/", include(router.urls)),
]
