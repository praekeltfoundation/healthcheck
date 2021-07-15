from django.contrib import admin
from django.urls import include, path  # noqa: F401
from rest_framework import routers

from selfswab.urls import v2router as selfswab_v2router
from tbconnect.urls import v2router as tbcheck_v2router
from lifenet.urls import v2router as lncheck_v2router
from vaccine.urls import v2router as vaccine_v2router

from userprofile.urls import v2router as userprofile_v2router
from userprofile.urls import v3router, v4router, v5router

global_v2router = routers.DefaultRouter()
global_v2router.registry.extend(userprofile_v2router.registry)
global_v2router.registry.extend(tbcheck_v2router.registry)
global_v2router.registry.extend(lncheck_v2router.registry)
global_v2router.registry.extend(selfswab_v2router.registry)
global_v2router.registry.extend(vaccine_v2router.registry)

urlpatterns = [
    path("prometheus/", include("django_prometheus.urls")),
    path("ht/", include("health_check.urls")),
    path("admin/", admin.site.urls),
    path("v1/", include("contacts.urls", namespace="api")),
    path("v1/", include("selfswab.urls", namespace="api2")),
    path("v2/", include(global_v2router.urls)),
    path("v3/", include(v3router.urls)),
    path("v4/", include(v4router.urls)),
    path("v5/", include(v5router.urls)),
]
