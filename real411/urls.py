from rest_framework import routers

from real411.views import ComplaintViewSet

v2router = routers.DefaultRouter()
v2router.register("real411/complaint", ComplaintViewSet)
