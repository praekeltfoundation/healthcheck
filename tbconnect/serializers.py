from rest_framework import serializers

from userprofile.serializers import BaseEventSerializer

from .models import TBCheck, TBTest


class TBCheckSerializer(BaseEventSerializer):
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


class TBTestSerializer(BaseEventSerializer):
    class Meta:
        model = TBTest
        fields = "__all__"
        read_only_fields = ("id", "created_by")
