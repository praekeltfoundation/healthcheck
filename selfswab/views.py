from django.http import JsonResponse
import random
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
    all_options = set(["CV%04dH" % i for i in range(0, 10000)])
    existing_contact_ids = set(
        SelfSwabScreen.objects.values("contact_id")
        .distinct()
        .values_list("contact_id", flat=True)
    )

    try:
        contact_id = random.choice(list(all_options - existing_contact_ids))
    except IndexError:
        contact_id = "-1"

    return JsonResponse({"id": contact_id})
