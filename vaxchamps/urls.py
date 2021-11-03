from rest_framework import routers
from vaxchamps.views import RegistrationViewSet

router = routers.DefaultRouter()
router.register("registrations", RegistrationViewSet, basename="registrations")

urlpatterns = router.urls
