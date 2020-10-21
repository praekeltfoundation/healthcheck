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
