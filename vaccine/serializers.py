import uuid

import phonenumbers
from rest_framework import serializers

from vaccine.models import VaccineRegistration
from userprofile.serializers import BaseEventSerializer, MSISDNField


class VaccineRegistrationSerializer(BaseEventSerializer):
    msisdn = MSISDNField(country="ZA")
    deduplication_id = serializers.CharField(default=uuid.uuid4, max_length=255)

    class Meta:
        model = VaccineRegistration
        fields = (
            "id",
            "deduplication_id",
            "msisdn",
            "source",
            "gender",
            "first_name",
            "last_name",
            "date_of_birth",
            "preferred_time",
            "preferred_date",
            "preferred_location_id",
            "preferred_location_name",
            "id_number",
            "refugee_number",
            "passport_number",
            "passport_country",
            "timestamp",
            "created_by",
            "data",
        )
        read_only_fields = ("id", "created_by")
