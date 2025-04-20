from django.urls import path, include
from rest_framework import routers
from .views.user import UserViewSet
from .views.car import CarViewSet

router = routers.DefaultRouter()
router.register(r"users", UserViewSet, basename="users")
router.register(r"cars", CarViewSet, basename="cars")

app_name = "user"
urlpatterns = [
    path("api/v1/", include(router.urls)),
]
