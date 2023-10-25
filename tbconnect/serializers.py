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

        activation = data.get("activation")

        if data.get("source") == "USSD":
            return data

        if activation:
            if not activation.startswith("tb_study"):
                if not data.get("location") and not data.get("city_location"):
                    raise serializers.ValidationError(
                        "location and city_location are both None"
                    )
        else:
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
    CLI = PhoneNumberField(required=True)
    Name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    Language = serializers.CharField(required=True)
    TB_Risk = serializers.CharField(required=True)
    Responded = serializers.CharField(required=True)
    TB_Tested = serializers.CharField(required=True)
    TB_Test_Results = serializers.CharField(required=True)
    Screen_timeStamp = serializers.CharField(required=True)
    Opt_In = serializers.CharField(required=True, allow_blank=True, allow_null=True)
    Drop_Off = serializers.CharField(required=True, allow_blank=True, allow_null=True)
    TB_Test_Results_Desc = serializers.CharField(
        required=True, allow_blank=True, allow_null=True
    )
