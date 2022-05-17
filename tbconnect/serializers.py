from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from userprofile.models import HealthCheckUserProfile
from userprofile.serializers import (
    BaseEventSerializer,
    HealthCheckUserProfileSerializer,
)

from .models import TBCheck, TBTest


class TBCheckSerializer(BaseEventSerializer):
    profile = serializers.SerializerMethodField()

    class Meta:
        model = TBCheck
        fields = "__all__"
        read_only_fields = ("id", "created_by")

    def validate(self, data):
        if data.get("age") == "<18":
            return data
        if not data.get("location") and not data.get("city_location"):
            raise serializers.ValidationError(
                "location and city_location are both None"
            )
        return data

    @extend_schema_field(HealthCheckUserProfileSerializer)
    def get_profile(self, obj):
        profile = HealthCheckUserProfile.objects.get_or_prefill(msisdn=obj.msisdn)
        return HealthCheckUserProfileSerializer(profile, many=False).data


class TBTestSerializer(BaseEventSerializer):
    class Meta:
        model = TBTest
        fields = "__all__"
        read_only_fields = ("id", "created_by")
