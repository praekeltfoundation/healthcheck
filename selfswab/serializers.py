from userprofile.serializers import BaseEventSerializer

from .models import SelfSwabRegistration, SelfSwabScreen, SelfSwabTest
from .utils import get_next_unique_contact_id, is_barcode_format_valid
from contacts.exceptions import CustomBadRequest
from rest_framework import serializers


class SelfSwabRegistrationSerializer(BaseEventSerializer):
    class Meta:
        model = SelfSwabRegistration
        fields = "__all__"
        read_only_fields = ("id", "created_by")

    def create(self, validated_data):
        if "contact_id" not in validated_data:
            validated_data["contact_id"] = get_next_unique_contact_id()
        return super().create(validated_data)


class SelfSwabScreenSerializer(BaseEventSerializer):
    class Meta:
        model = SelfSwabScreen
        fields = "__all__"
        read_only_fields = ("id", "created_by")


class SelfSwabTestSerializer(BaseEventSerializer):
    def validate(self, data):
        barcode = data.get("barcode")
        if not is_barcode_format_valid(barcode):
            raise CustomBadRequest("barcode invalid format.")
        return super(SelfSwabTestSerializer, self).validate(data)

    class Meta:
        model = SelfSwabTest
        fields = "__all__"
        read_only_fields = ("id", "created_by")


class GetBarcodeFromLastInboundImageSerializer(serializers.Serializer):
    wa_id = serializers.CharField()


class WhitelistContactSerializer(serializers.Serializer):
    msisdn = serializers.CharField()
    whitelist_group_uuid = serializers.CharField()


class SendTestResultPDFSerializer(serializers.Serializer):
    barcode = serializers.CharField()
