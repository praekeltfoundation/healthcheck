from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.mixins import CreateModelMixin, UpdateModelMixin
from rest_framework.permissions import DjangoModelPermissions
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ViewSet
from temba_client.v2 import TembaClient

from userprofile.models import HealthCheckUserProfile
from userprofile.serializers import HealthCheckUserProfileSerializer, MSISDNSerializer

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


class TBResetViewSet(ViewSet):
    serializer_class = MSISDNSerializer
    renderer_classes = [TemplateHTMLRenderer]
    template_name = "tbreset.html"

    def get(self, request, pk):
        if pk not in settings.ALLOW_TB_RESET_MSISDNS:
            return Response(
                {"status": "NotInAllowed"}, status=status.HTTP_403_FORBIDDEN
            )
        profile = get_object_or_404(HealthCheckUserProfile, pk=pk)
        return Response({"profile": profile.msisdn})

    def destroy(self, request, pk=None):
        if pk not in settings.ALLOW_TB_RESET_MSISDNS:
            return Response(
                {"status": "NotInAllowed"}, status=status.HTTP_403_FORBIDDEN
            )

        profile = get_object_or_404(HealthCheckUserProfile, pk=pk)
        profile.delete()
        TBCheck.objects.filter(msisdn=pk).delete()
        rapidpro = TembaClient(settings.RAPIDPRO_URL, settings.RAPIDPRO_TOKEN)
        rapidpro.delete_contact(f"tel:{pk}")
        return Response({"status": "OK"})
