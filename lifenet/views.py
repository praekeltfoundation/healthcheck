from rest_framework.mixins import CreateModelMixin, UpdateModelMixin
from rest_framework.permissions import DjangoModelPermissions
from rest_framework.viewsets import GenericViewSet

from userprofile.models import HealthCheckUserProfile

from .models import LNCheck
from .serializers import LNCheckSerializer


class LNCheckViewSet(GenericViewSet, CreateModelMixin):
    queryset = LNCheck.objects.all()
    serializer_class = LNCheckSerializer
    permission_classes = (DjangoModelPermissions,)

    def perform_create(self, serializer):
        """
        Create or Update the user profile
        """
        instance = serializer.save()

        profile = HealthCheckUserProfile.objects.get_or_prefill(
            msisdn=instance.msisdn)
        profile.update_from_tbcheck(instance)
        profile.save()

        return instance
