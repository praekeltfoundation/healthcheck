from datetime import timedelta

from rest_framework import pagination, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from covid_cases.models import (
    District,
    Province,
    SACoronavirusCaseImage,
    SACoronavirusCounter,
    SubDistrict,
    Ward,
    WardCase,
)
from covid_cases.serializers import (
    DistrictSerializer,
    ProvinceSerializer,
    SACoronavirusCaseImageSerializer,
    SACoronavirusCounterSerializer,
    SubDistrictSerializer,
    WardCaseFlatSerializer,
    WardCaseSerializer,
    WardSerializer,
)
from covid_cases.utils import cache_method


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


class SACoronavirusCaseImageViewSet(viewsets.ModelViewSet):
    queryset = SACoronavirusCaseImage.objects.all()
    serializer_class = SACoronavirusCaseImageSerializer
    permissions_classes = [permissions.DjangoModelPermissionsOrAnonReadOnly]
    pagination_class = IdCursorPagination


class ContactNDoHCasesViewSet(viewsets.ViewSet):
    permissions_classes = [permissions.IsAuthenticatedOrReadOnly]

    @cache_method("latest_image", 60 * 60)
    def get_latest_image(self):
        # We cache the image so that the signed URL doesn't change too often, so that
        # the image can be cached
        image = SACoronavirusCaseImage.objects.latest("date")
        return SACoronavirusCaseImageSerializer(image).data

    def list(self, request):
        """
        Provides a combined and aggregated view of the latest case data that will be
        used for the CASES keyword on ContactNDoH
        """
        response = {"image": self.get_latest_image()}

        counter = SACoronavirusCounter.objects.latest("date")
        response["counter"] = SACoronavirusCounterSerializer(counter).data

        try:
            # If we have a day before's data, then we can include daily numbers
            last_counter = SACoronavirusCounter.objects.get(
                date=counter.date - timedelta(days=1)
            )
            response["daily"] = {
                "tests": counter.tests - last_counter.tests,
                "positive": counter.positive - last_counter.positive,
                "recoveries": counter.recoveries - last_counter.recoveries,
                "deaths": counter.deaths - last_counter.deaths,
                "vaccines": counter.vaccines - last_counter.vaccines,
            }
        except SACoronavirusCounter.DoesNotExist:
            pass

        return Response(response)
