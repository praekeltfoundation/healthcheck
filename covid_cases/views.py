from django.db.models import query
from rest_framework import pagination, permissions, viewsets
from rest_framework.decorators import action

from covid_cases.models import (
    District,
    Province,
    SACoronavirusCounter,
    SubDistrict,
    Ward,
    WardCase,
)
from covid_cases.serializers import (
    DistrictSerializer,
    ProvinceSerializer,
    SACoronavirusCounterSerializer,
    SubDistrictSerializer,
    WardCaseFlatSerializer,
    WardCaseSerializer,
    WardSerializer,
)


class IdCursorPagination(pagination.CursorPagination):
    ordering = "id"


class ProvinceViewSet(viewsets.ModelViewSet):
    queryset = Province.objects.all()
    serializer_class = ProvinceSerializer
    permission_classes = [permissions.DjangoModelPermissionsOrAnonReadOnly]
    pagination_class = IdCursorPagination


class DistrictViewSet(viewsets.ModelViewSet):
    queryset = District.objects.all()
    serializer_class = DistrictSerializer
    permission_classes = [permissions.DjangoModelPermissionsOrAnonReadOnly]
    pagination_class = IdCursorPagination


class SubDistrictViewSet(viewsets.ModelViewSet):
    queryset = SubDistrict.objects.all()
    serializer_class = SubDistrictSerializer
    permission_classes = [permissions.DjangoModelPermissionsOrAnonReadOnly]
    pagination_class = IdCursorPagination


class WardViewSet(viewsets.ModelViewSet):
    queryset = Ward.objects.all()
    serializer_class = WardSerializer
    permission_classes = [permissions.DjangoModelPermissionsOrAnonReadOnly]
    pagination_class = IdCursorPagination


class WardCaseViewSet(viewsets.ModelViewSet):
    queryset = WardCase.objects.all()
    serializer_class = WardCaseSerializer
    permission_classes = [permissions.DjangoModelPermissionsOrAnonReadOnly]
    pagination_class = IdCursorPagination

    @action(detail=False)
    def flat(self, request):
        page = self.paginate_queryset(
            self.get_queryset().select_related(
                "ward",
                "ward__sub_district",
                "ward__sub_district__district",
                "ward__sub_district__district__province",
            )
        )
        serializer = WardCaseFlatSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)


class SACoronavirusCounterViewSet(viewsets.ModelViewSet):
    queryset = SACoronavirusCounter.objects.all()
    serializer_class = SACoronavirusCounterSerializer
    permissions_classes = [permissions.DjangoModelPermissionsOrAnonReadOnly]
    pagination_class = IdCursorPagination
