from rest_framework.mixins import CreateModelMixin, UpdateModelMixin
from rest_framework.permissions import DjangoModelPermissions
from rest_framework.viewsets import GenericViewSet

from userprofile.models import HealthCheckUserProfile

from .models import TBCheck, TBTest
from .serializers import TBCheckSerializer, TBTestSerializer


class TBCheckViewSet(GenericViewSet, CreateModelMixin, UpdateModelMixin):
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

        # Only assign users to a group arm if they have high and moderate risk
        if instance.risk != "low":
            profile.update_tbconnect_group_arm()

        profile.save()

        return instance


class TBTestViewSet(GenericViewSet, CreateModelMixin, UpdateModelMixin):
    queryset = TBTest.objects.all()
    serializer_class = TBTestSerializer
    permission_classes = (DjangoModelPermissions,)
