from django.contrib import admin
from django.urls import include, path  # noqa: F401
from rest_framework import routers

from tbconnect.urls import v2router as tbcheck_v2router
from userprofile.urls import v2router as userprofile_v2router
from userprofile.urls import v3router, v4router

global_v2router = routers.DefaultRouter()
global_v2router.registry.extend(userprofile_v2router.registry)
global_v2router.registry.extend(tbcheck_v2router.registry)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("v1/", include("contacts.urls", namespace="api")),
    path("v2/", include(global_v2router.urls)),
    path("v3/", include(v3router.urls)),
    path("v4/", include(v4router.urls)),
]
