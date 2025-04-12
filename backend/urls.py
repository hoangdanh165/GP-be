from django.contrib import admin
from django.urls import path, include, re_path
from django.http import HttpResponse, HttpResponseServerError


def hello_world(request):
    return HttpResponse("hello world")


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", hello_world),
    path("", include("user.urls")),
    path("", include("chat.urls")),
    path("", include("service.urls")),
    path("", include("notification.urls")),
]
