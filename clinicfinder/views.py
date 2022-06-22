from django.conf import settings
from .models import Location
from rest_framework import generics, permissions, status
from .serializers import LocationSerializer
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from rest_framework.response import Response
from rest_framework.mixins import ListModelMixin
from django.contrib.gis.db.models.functions import Distance
from django.http import JsonResponse


class ClinicFinderView(generics.GenericAPIView, ListModelMixin):
    serializer_class = LocationSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        distance_range = settings.LOCATION_SEARCH_RADIUS
        params = request.query_params
        if "longitude" in params and "latitude" in params:
            long = float(params.get("longitude"))
            lat = float(params.get("latitude"))

            point = Point(long, lat)
            locations = (
                Location.objects.filter(
                    location__distance_lte=(point, D(km=distance_range))
                )
                .annotate(distance=Distance("location", point))
                .order_by("distance")[:5]
            )

            return JsonResponse(
                {"locations": LocationSerializer(locations, many=True).data},
                status=status.HTTP_200_OK,
            )
        return Response(
            {"error": "longitude and latitude are required"},
            status=status.HTTP_400_BAD_REQUEST,
        )
