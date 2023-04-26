from rest_framework import routers

from tbconnect.views import (
    TBCheckViewSet,
    TBResetViewSet,
    TBTestViewSet,
    TBCheckCciDataViewSet,
)

v2router = routers.DefaultRouter()
v2router.register("tbcheck", TBCheckViewSet)
v2router.register("tbtest", TBTestViewSet)
v2router.register("tbreset", TBResetViewSet, basename="tbreset")
v2router.register("tbcheckccidata", TBCheckCciDataViewSet, basename="tbcheckccidata")
