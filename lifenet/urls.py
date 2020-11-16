from rest_framework import routers

from lifenet.views import LNCheckViewSet

v2router = routers.DefaultRouter()
v2router.register("lncheck", LNCheckViewSet)
