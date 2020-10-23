from django.urls import path
from rest_framework import routers

from selfswab.views import SelfSwabScreenViewSet, SelfSwabTestViewSet, unique_contact_id

v2router = routers.DefaultRouter()
v2router.register("selfswabscreen", SelfSwabScreenViewSet)
v2router.register("selfswabtest", SelfSwabTestViewSet)

urlpatterns = [
    path("unique_contact_id", unique_contact_id, name="unique_contact_id"),
]
