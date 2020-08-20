from django.contrib import admin
from django.urls import include, path  # noqa: F401

from userprofile.urls import v2router, v3router, v4router

urlpatterns = [
    path("admin/", admin.site.urls),
    path("v1/", include("contacts.urls", namespace="api")),
    path("v2/", include(v2router.urls)),
    path("v3/", include(v3router.urls)),
    path("v4/", include(v4router.urls)),
]
