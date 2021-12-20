from rest_framework import routers

from real411.views import ComplaintViewSet, ComplaintUpdateViewSet

v2router = routers.DefaultRouter()
v2router.register("real411/complaint", ComplaintViewSet)
v2router.register(
    "real411/update_complaint", ComplaintUpdateViewSet, basename="update_complaint"
)
