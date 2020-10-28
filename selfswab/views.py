from rest_framework.mixins import CreateModelMixin
from rest_framework.permissions import DjangoModelPermissions
from rest_framework.viewsets import GenericViewSet

from .models import SelfSwabRegistration, SelfSwabScreen, SelfSwabTest
from .serializers import (
    SelfSwabRegistrationSerializer,
    SelfSwabScreenSerializer,
    SelfSwabTestSerializer,
)


class SelfSwabScreenViewSet(GenericViewSet, CreateModelMixin):
    queryset = SelfSwabScreen.objects.all()
    serializer_class = SelfSwabScreenSerializer
    permission_classes = (DjangoModelPermissions,)


class SelfSwabTestViewSet(GenericViewSet, CreateModelMixin):
    queryset = SelfSwabTest.objects.all()
    serializer_class = SelfSwabTestSerializer
    permission_classes = (DjangoModelPermissions,)


class SelfSwabRegistrationViewSet(GenericViewSet, CreateModelMixin):
    queryset = SelfSwabRegistration.objects.all()
    serializer_class = SelfSwabRegistrationSerializer
    permission_classes = (DjangoModelPermissions,)
