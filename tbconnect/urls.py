from rest_framework import routers

from tbconnect.views import TBCheckViewSet, TBTestViewSet

v2router = routers.DefaultRouter()
v2router.register("tbcheck", TBCheckViewSet)
v2router.register("tbtest", TBTestViewSet)
