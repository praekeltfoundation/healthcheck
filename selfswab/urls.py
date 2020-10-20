from rest_framework import routers

from selfswab.views import SelfSwabScreenViewSet, SelfSwabTestViewSet

v2router = routers.DefaultRouter()
v2router.register("selfswabscreen", SelfSwabScreenViewSet)
v2router.register("selfswabtest", SelfSwabTestViewSet)
