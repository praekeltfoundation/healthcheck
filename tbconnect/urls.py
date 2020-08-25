from rest_framework import routers

from tbconnect.views import TBCheckViewSet

v2router = routers.DefaultRouter()
v2router.register("tbcheck", TBCheckViewSet)
