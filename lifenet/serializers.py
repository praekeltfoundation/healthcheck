from rest_framework import serializers

from userprofile.serializers import BaseEventSerializer

from .models import LNCheck


class LNCheckSerializer(BaseEventSerializer):
    class Meta:
        model = TBCheck
        fields = "__all__"
        read_only_fields = ("id", "created_by")
