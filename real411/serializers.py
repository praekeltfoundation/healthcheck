from rest_framework import serializers
from real411.models import Complaint


class ComplaintSerializer(serializers.ModelSerializer):
    class Meta:
        model = Complaint
        fields = ["id", "complaint_ref", "msisdn", "created_at", "updated_at"]


class ComplaintUpdateSerializer(serializers.Serializer):
    complaint_ref = serializers.CharField(
        max_length=255, help_text="The complaint reference"
    )
    is_duplicate = serializers.BooleanField(
        help_text="If the complaint has been marked as duplicate"
    )
    title = serializers.CharField(
        max_length=255,
        allow_null=True,
        help_text="Complaint title. Null if not relevant or not yet resolved",
    )
    overview = serializers.CharField(
        max_length=65535,
        allow_null=True,
        help_text="Complaint overview. Null if not relevant or not yet resolved",
    )
    background_ruiling = serializers.CharField(
        max_length=65535,
        allow_null=True,
        help_text="Background and final ruling. Null if not relevant or not yet resolved",
    )
    real411_backlink = serializers.URLField(
        max_length=255, help_text="Link to the complaint on the Real411 website"
    )

    class Status(serializers.Serializer):
        id = serializers.IntegerField()
        code = serializers.CharField(max_length=255)
        name = serializers.CharField(max_length=255)
        description = serializers.CharField(max_length=65535)

    status = Status()
