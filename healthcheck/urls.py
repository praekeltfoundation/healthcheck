from django.contrib import admin
from django.urls import include, path  # noqa: F401

urlpatterns = [
    path("admin/", admin.site.urls),
    path("v1/", include("contacts.urls", namespace="api")),
]
