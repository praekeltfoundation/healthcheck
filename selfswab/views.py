from django.http import JsonResponse
from random import randint
from rest_framework.mixins import CreateModelMixin
from rest_framework.permissions import DjangoModelPermissions
from rest_framework.viewsets import GenericViewSet

from .models import SelfSwabScreen, SelfSwabTest
from .serializers import SelfSwabScreenSerializer, SelfSwabTestSerializer


class SelfSwabScreenViewSet(GenericViewSet, CreateModelMixin):
    queryset = SelfSwabScreen.objects.all()
    serializer_class = SelfSwabScreenSerializer
    permission_classes = (DjangoModelPermissions,)


class SelfSwabTestViewSet(GenericViewSet, CreateModelMixin):
    queryset = SelfSwabTest.objects.all()
    serializer_class = SelfSwabTestSerializer
    permission_classes = (DjangoModelPermissions,)


def unique_contact_id(request):
    while True:
        contact_id = "CV%04dH" % randint(0, 9999)

        if not SelfSwabScreen.objects.filter(contact_id=contact_id).exists():
            break

    return JsonResponse({"id": contact_id})
