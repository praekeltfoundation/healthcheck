from rest_framework.mixins import CreateModelMixin
from rest_framework.permissions import DjangoModelPermissions
from rest_framework.viewsets import GenericViewSet

from .models import TBCheck
from .serializers import TBCheckSerializer


class TBCheckViewSet(GenericViewSet, CreateModelMixin):
    queryset = TBCheck.objects.all()
    serializer_class = TBCheckSerializer
    permission_classes = (DjangoModelPermissions,)
