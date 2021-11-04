from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import status, viewsets
from rest_framework.permissions import DjangoModelPermissions
from rest_framework.response import Response
from temba_client.v2 import TembaClient

from vaxchamps.serializers import (
    AGES,
    DISTRICTS,
    GENDERS,
    LANGUAGES,
    PROVINCES,
    RegistrationSerializer,
)

rapidpro_client = TembaClient(settings.RAPIDPRO_URL, settings.RAPIDPRO_TOKEN)


class CreateRegistrationPermissions(DjangoModelPermissions):
    perms_map = {"POST": ["vaxchamps.create_registration"]}
    authenticated_users_only = True


class RegistrationViewSet(viewsets.ViewSet):
    serializer_class = RegistrationSerializer
    permission_classes = [CreateRegistrationPermissions]
    queryset = get_user_model().objects.none()

    def start_rapidpro_flow(self, data):
        data = data.copy()
        urn = f"whatsapp:{data['cell_no'].lstrip('+')}"
        data["lang"] = LANGUAGES[data["lang"]]
        if data.get("province"):
            data["province"] = PROVINCES[data["province"]]["name"]
        if data.get("district"):
            data["district"] = DISTRICTS[data["district"]]
        if data.get("gender"):
            data["gender"] = GENDERS[data["gender"]]
        if data.get("age"):
            data["age"] = AGES[data["age"]]
        rapidpro_client.create_flow_start(
            settings.VAXCHAMPS_RAPIDPRO_FLOW, urns=[urn], extra=data
        )

    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.start_rapidpro_flow(serializer.data)
        return Response(serializer.data, status.HTTP_201_CREATED)
