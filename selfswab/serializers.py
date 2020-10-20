from userprofile.serializers import BaseEventSerializer

from .models import SelfSwabScreen, SelfSwabTest


class SelfSwabScreenSerializer(BaseEventSerializer):
    class Meta:
        model = SelfSwabScreen
        fields = "__all__"
        read_only_fields = ("id", "created_by")


class SelfSwabTestSerializer(BaseEventSerializer):
    class Meta:
        model = SelfSwabTest
        fields = "__all__"
        read_only_fields = ("id", "created_by")
