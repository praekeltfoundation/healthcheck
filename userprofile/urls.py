from rest_framework import routers

from userprofile.views import (
    Covid19TriageV2ViewSet,
    Covid19TriageV3ViewSet,
    Covid19TriageViewSet,
    HealthCheckUserProfileViewSet,
)

v2router = routers.DefaultRouter()
v2router.register("healthcheckuserprofile", HealthCheckUserProfileViewSet)
v2router.register("covid19triage", Covid19TriageViewSet)

v3router = routers.DefaultRouter()
v3router.register("covid19triage", Covid19TriageV2ViewSet, basename="covid19triagev2")

v4router = routers.DefaultRouter()
v4router.register("covid19triage", Covid19TriageV3ViewSet, basename="covid19triagev3")
