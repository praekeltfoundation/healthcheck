from django.db import IntegrityError
from django.http import Http404
from django_filters import rest_framework as filters
from rest_framework import status
from rest_framework.mixins import (
    CreateModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
)
from rest_framework.pagination import CursorPagination
from rest_framework.permissions import DjangoModelPermissions
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from userprofile.models import Covid19Triage, HealthCheckUserProfile
from userprofile.serializers import (
    Covid19TriageSerializer,
    Covid19TriageV2Serializer,
    Covid19TriageV3Serializer,
    Covid19TriageV4Serializer,
    HealthCheckUserProfileSerializer,
    MSISDNSerializer,
)


class Covid19TriageFilter(filters.FilterSet):
    timestamp_gt = filters.IsoDateTimeFilter(field_name="timestamp", lookup_expr="gt")

    class Meta:
        model = Covid19Triage
        fields: list = []


def CursorPaginationFactory(field):
    """
    Returns a CursorPagination class with the field specified by field
    """

    class CustomCursorPagination(CursorPagination):
        ordering = field

    name = "{}CursorPagination".format(field.capitalize())
    CustomCursorPagination.__name__ = name
    CustomCursorPagination.__qualname__ = name

    return CustomCursorPagination


class Covid19TriageViewSet(GenericViewSet, CreateModelMixin, ListModelMixin):
    queryset = Covid19Triage.objects.all()
    serializer_class = Covid19TriageSerializer
    permission_classes = (DjangoModelPermissions,)
    pagination_class = CursorPaginationFactory("timestamp")
    filter_backends = [filters.DjangoFilterBackend]
    filterset_class = Covid19TriageFilter

    def perform_create(self, serializer):
        """
        Mark turn healthcheck complete, and update the user profile
        """
        instance = serializer.save()

        profile = HealthCheckUserProfile.objects.get_or_prefill(msisdn=instance.msisdn)
        profile.update_from_healthcheck(instance)
        profile.save()

        return instance

    def create(self, *args, **kwargs):
        try:
            return super().create(*args, **kwargs)
        except IntegrityError:
            # We already have this entry
            return Response(status=status.HTTP_200_OK)

    def get_throttles(self):
        """
        Set the throttle_scope dynamically to get different rates per action
        """
        self.throttle_scope = f"covid19triage.{self.action}"
        return super().get_throttles()


class Covid19TriageV2ViewSet(Covid19TriageViewSet):
    serializer_class = Covid19TriageV2Serializer
    returning_user_skipped_fields = {
        "first_name",
        "last_name",
        "province",
        "city",
        "date_of_birth",
        "gender",
        "location",
        "city_location",
        "preexisting_condition",
        "rooms_in_household",
        "persons_in_household",
    }

    def _get_msisdn(self, data):
        """Gets the MSISDN from the data, or raises a ValidationError"""
        serializer = MSISDNSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        return serializer.validated_data["msisdn"]

    def _update_data(self, data, triage):
        """Updates the data from the values in triage"""
        for field in self.returning_user_skipped_fields:
            value = getattr(triage, field)
            if value:
                data[field] = value

    def create(self, request, *args, **kwargs):
        # If all of the returning user skipped fields are missing
        if all(not request.data.get(f) for f in self.returning_user_skipped_fields):
            # Get those fields from a previous completed HealthCheck
            msisdn = self._get_msisdn(request.data)
            triage = Covid19Triage.objects.filter(msisdn=msisdn).earliest("timestamp")
            if triage:
                self._update_data(request.data, triage)
        return super().create(request, *args, **kwargs)


class Covid19TriageV3ViewSet(Covid19TriageV2ViewSet):
    serializer_class = Covid19TriageV3Serializer

    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)


class Covid19TriageV4ViewSet(Covid19TriageV3ViewSet):
    serializer_class = Covid19TriageV4Serializer

    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)


class HealthCheckUserProfileViewSet(
    GenericViewSet, RetrieveModelMixin, UpdateModelMixin
):
    queryset = HealthCheckUserProfile.objects.all()
    serializer_class = HealthCheckUserProfileSerializer
    permission_classes = (DjangoModelPermissions,)

    def get_object(self):
        obj = HealthCheckUserProfile.objects.get_or_prefill(msisdn=self.kwargs["pk"])
        if not obj.pk:
            raise Http404()
        self.check_object_permissions(self.request, obj)
        return obj
