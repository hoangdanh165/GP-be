from django.urls import path, include
from rest_framework import routers
from .views.payment import PaymentViewSet

router = routers.DefaultRouter()
router.register(r"payments", PaymentViewSet, basename="payments")

app_name = "payment"
urlpatterns = [
    path("api/v1/", include(router.urls)),
]
