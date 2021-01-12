from rest_framework import generics, permissions, status
from rest_framework.mixins import CreateModelMixin, UpdateModelMixin
from rest_framework.permissions import DjangoModelPermissions
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from temba_client.v2 import TembaClient
from django.conf import settings

from .models import SelfSwabRegistration, SelfSwabScreen, SelfSwabTest
from .serializers import (
    SelfSwabRegistrationSerializer,
    SelfSwabScreenSerializer,
    SelfSwabTestSerializer,
)
from .utils import send_whatsapp_media_message


class SelfSwabScreenViewSet(GenericViewSet, CreateModelMixin):
    queryset = SelfSwabScreen.objects.all()
    serializer_class = SelfSwabScreenSerializer
    permission_classes = (DjangoModelPermissions,)


class SelfSwabTestViewSet(GenericViewSet, CreateModelMixin):
    queryset = SelfSwabTest.objects.all()
    serializer_class = SelfSwabTestSerializer
    permission_classes = (DjangoModelPermissions,)


class SelfSwabRegistrationViewSet(GenericViewSet, CreateModelMixin, UpdateModelMixin):
    queryset = SelfSwabRegistration.objects.all()
    serializer_class = SelfSwabRegistrationSerializer
    permission_classes = (DjangoModelPermissions,)


class WhitelistContactView(generics.GenericAPIView):
    """
    POST endpoint to whitelist a contact.
    ---
    POST fields:
    * msisdn
    * whitelist_group_uuid
    """

    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        data = request.data

        msisdn = data.pop("msisdn", None)
        whitelist_group_uuid = data.pop("whitelist_group_uuid", None)

        if settings.RAPIDPRO_URL and settings.SELFSWAB_RAPIDPRO_TOKEN:
            rapidpro = TembaClient(
                settings.RAPIDPRO_URL, settings.SELFSWAB_RAPIDPRO_TOKEN
            )

            contact = rapidpro.get_contacts(urn=f"whatsapp:{msisdn}").first()

            if contact:
                group_ids = [g.uuid for g in contact.groups]

                if whitelist_group_uuid in group_ids:
                    return Response(
                        {"error": "already whitelisted"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                else:
                    groups = contact.groups
                    groups.append(whitelist_group_uuid)
                    rapidpro.update_contact(contact, groups=groups)

                    return Response({}, status=status.HTTP_200_OK)
            else:
                rapidpro.create_contact(
                    language="eng",
                    fields={"msisdn": msisdn},
                    groups=[whitelist_group_uuid],
                    urns=[f"whatsapp:{msisdn}"],
                )

                return Response({}, status=status.HTTP_201_CREATED)

        return Response(
            {"error": "rapidpro not configured"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


class SendTestResultPDFView(generics.GenericAPIView):
    """
    POST endpoint send test result PDF to contact.
    ---
    POST fields:
    * barcode
    """

    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        data = request.data

        barcode = data.pop("barcode", None)

        try:
            test = SelfSwabTest.objects.get(barcode=barcode)
        except SelfSwabTest.DoesNotExist:
            return Response({}, status=status.HTTP_404_NOT_FOUND)

        send_whatsapp_media_message(test.msisdn, "document", test.pdf_media_id)

        return Response({}, status=status.HTTP_200_OK)
