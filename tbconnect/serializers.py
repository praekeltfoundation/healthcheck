from userprofile.serializers import BaseEventSerializer

from .models import TBCheck


class TBCheckSerializer(BaseEventSerializer):
    class Meta:
        model = TBCheck
        fields = "__all__"
        read_only_fields = ("id", "created_by")
