from rest_framework import routers

from selfswab.views import (
    SelfSwabRegistrationViewSet,
    SelfSwabScreenViewSet,
    SelfSwabTestViewSet,
)

v2router = routers.DefaultRouter()
v2router.register("selfswabscreen", SelfSwabScreenViewSet)
v2router.register("selfswabtest", SelfSwabTestViewSet)
v2router.register("selfswabregistration", SelfSwabRegistrationViewSet)
