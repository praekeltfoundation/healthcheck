from userprofile.serializers import BaseEventSerializer

from .models import SelfSwabRegistration, SelfSwabScreen, SelfSwabTest
from .utils import get_next_unique_contact_id


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
    class Meta:
        model = SelfSwabTest
        fields = "__all__"
        read_only_fields = ("id", "created_by")
