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
        profile.update_tbconnect_group_arm()
        profile.save()

        return instance

    def perform_update(self, serializer):
        """
        To update commit_get_tested to an existing TBCheck
        """
        instance = serializer.save()

        if instance.commit_get_tested:
            tbcheck = TBCheck.objects.filter(msisdn=instance.msisdn).last()
            tbcheck.commit_get_tested = instance.commit_get_tested
            tbcheck.save()

        return instance


class TBTestViewSet(GenericViewSet, CreateModelMixin, UpdateModelMixin):
    queryset = TBTest.objects.all()
    serializer_class = TBTestSerializer
    permission_classes = (DjangoModelPermissions,)

