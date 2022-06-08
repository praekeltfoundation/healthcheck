from django.contrib import admin
from django.urls import include, path  # noqa: F401
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import routers
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from selfswab.urls import v2router as selfswab_v2router
from tbconnect.urls import v2router as tbcheck_v2router
from lifenet.urls import v2router as lncheck_v2router
from vaccine.urls import v2router as vaccine_v2router
from covid_cases.urls import v2router as covidcases_v2router
from real411.urls import v2router as real411_v2router

from userprofile.urls import v2router as userprofile_v2router
from userprofile.urls import v3router, v4router, v5router

global_v2router = routers.DefaultRouter()
global_v2router.registry.extend(userprofile_v2router.registry)
global_v2router.registry.extend(tbcheck_v2router.registry)
global_v2router.registry.extend(lncheck_v2router.registry)
global_v2router.registry.extend(selfswab_v2router.registry)
global_v2router.registry.extend(vaccine_v2router.registry)
global_v2router.registry.extend(covidcases_v2router.registry)
global_v2router.registry.extend(real411_v2router.registry)

urlpatterns = [
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path("docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("prometheus/", include("django_prometheus.urls")),
    path("ht/", include("health_check.urls")),
    path("admin/", admin.site.urls),
    path("v1/", include("contacts.urls", namespace="api")),
    path("v1/", include("selfswab.urls", namespace="api2")),
    path("v1/", include("clinicfinder.urls")),
    path("v2/", include(global_v2router.urls)),
    path("v3/", include(v3router.urls)),
    path("v4/", include(v4router.urls)),
    path("api/v5/", include(v5router.urls)),
    path("v1/vaxchamps/", include("vaxchamps.urls")),
]

# Need to add this for media files to work for development
# Django defaults to sending static files in dev mode, but not media files
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
