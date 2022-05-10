from rest_framework import routers

from tbconnect.views import TBCheckViewSet, TBTestViewSet, TBTestCommitViewSet

v2router = routers.DefaultRouter()
v2router.register("tbcheck", TBCheckViewSet)
v2router.register("tbtest", TBTestViewSet)
v2router.register("tbtestcommit", TBTestCommitViewSet)
