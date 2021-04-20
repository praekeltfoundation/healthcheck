from rest_framework import routers

from vaccine.views import VaccineRegistrationViewSet

v2router = routers.DefaultRouter()
v2router.register("vaccineregistration", VaccineRegistrationViewSet)
