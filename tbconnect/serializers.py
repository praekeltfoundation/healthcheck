from rest_framework import serializers

from userprofile.serializers import BaseEventSerializer

from .models import TBCheck


class TBCheckSerializer(BaseEventSerializer):
    class Meta:
        model = TBCheck
        fields = "__all__"
        read_only_fields = ("id", "created_by")

    def validate(self, data):
        if not data.get("location") and not data.get("city_location"):
            raise serializers.ValidationError(
                "location and city_location are both None"
            )
        return data
