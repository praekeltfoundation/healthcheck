from rest_framework.mixins import CreateModelMixin
from rest_framework.permissions import DjangoModelPermissions
from rest_framework.viewsets import GenericViewSet

from userprofile.models import HealthCheckUserProfile

from .models import TBCheck
from .serializers import TBCheckSerializer


class TBCheckViewSet(GenericViewSet, CreateModelMixin):
    queryset = TBCheck.objects.all()
    serializer_class = TBCheckSerializer
    permission_classes = (DjangoModelPermissions,)

    def perform_create(self, serializer):
        """
        Create or Update the user profile
        """
        instance = serializer.save()

        profile = HealthCheckUserProfile.objects.get_or_prefill(msisdn=instance.msisdn)
        profile.update_from_tbcheck(instance)
        profile.save()

        return instance
