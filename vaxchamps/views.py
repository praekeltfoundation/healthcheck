from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import DjangoModelPermissions
from vaxchamps.serializers import RegistrationSerializer
from django.contrib.auth import get_user_model


class CreateRegistrationPermissions(DjangoModelPermissions):
    perms_map = {"POST": ["vaxchamps.create_registration"]}
    authenticated_users_only = True


class RegistrationViewSet(viewsets.ViewSet):
    serializer_class = RegistrationSerializer
    permission_classes = [CreateRegistrationPermissions]
    queryset = get_user_model().objects.none()

    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status.HTTP_201_CREATED)
