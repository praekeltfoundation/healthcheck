from django.urls import path
from rest_framework import routers

from tbconnect.views import (
    TBActivationStatusViewSet,
    TBCheckViewSet,
    TBResetViewSet,
    TBTestViewSet,
    TBCheckCciDataViewSet,
)

app_name = "tbconnect"

v2router = routers.DefaultRouter()
v2router.register("tbcheck", TBCheckViewSet)
v2router.register("tbtest", TBTestViewSet)
v2router.register("tbreset", TBResetViewSet, basename="tbreset")
v2router.register("tbcheckccidata", TBCheckCciDataViewSet, basename="tbcheckccidata")

urlpatterns = [
    path(
        "tbactivationstatus",
        TBActivationStatusViewSet.as_view(),
        name="tbactivationstatus",
    ),
]
