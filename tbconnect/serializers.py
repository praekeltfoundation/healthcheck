from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from userprofile.models import HealthCheckUserProfile
from userprofile.serializers import (
    BaseEventSerializer,
    HealthCheckUserProfileSerializer,
)

from .models import TBCheck, TBTest
from phonenumber_field.serializerfields import PhoneNumberField


class TBCheckSerializer(BaseEventSerializer):
    profile = serializers.SerializerMethodField()

    class Meta:
        model = TBCheck
        fields = "__all__"
        read_only_fields = ("id", "created_by")

    def validate(self, data):
        if data.get("age") == "<18":
            return data
        if data.get("source") != "USSD":
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


class TBCheckCciDataSerializer(serializers.Serializer):
    msisdn = PhoneNumberField(required=True)
    name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    language = serializers.CharField(required=True)
    tb_risk = serializers.CharField(required=True)
    responded = serializers.CharField(required=True)
    tb_tested = serializers.CharField(required=True)
    tb_test_results = serializers.CharField(required=True)
    screen_timeStamp = serializers.CharField(required=True)
