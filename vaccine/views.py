from django.db import IntegrityError
from django.shortcuts import render

from rest_framework import status
from rest_framework.mixins import CreateModelMixin
from rest_framework.permissions import DjangoModelPermissions
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from vaccine.models import VaccineRegistration
from vaccine.serializers import VaccineRegistrationSerializer


class VaccineRegistrationViewSet(GenericViewSet, CreateModelMixin):
    queryset = VaccineRegistration.objects.all()
    serializer_class = VaccineRegistrationSerializer
    permission_classes = (DjangoModelPermissions,)

    def create(self, *args, **kwargs):
        try:
            return super().create(*args, **kwargs)
        except IntegrityError:
            # We already have this entry
            return Response(status=status.HTTP_200_OK)
