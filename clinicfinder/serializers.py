from .models import Location
from rest_framework import serializers
from rest_framework_gis.serializers import GeoModelSerializer


class LocationSerializer(GeoModelSerializer):
    """A class to serialize locations"""

    longitude = serializers.FloatField(required=True)
    latitude = serializers.FloatField(required=True)

    class Meta:
        model = Location
        geo_field = "point"
        fields = "__all__"
