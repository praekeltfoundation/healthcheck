import uuid

import phonenumbers
from rest_framework import serializers

from userprofile.models import Covid19Triage, HealthCheckUserProfile


class BaseEventSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        validated_data["created_by"] = self.context["request"].user.username
        return super().create(validated_data)


class MSISDNField(serializers.CharField):
    """
    A phone number, validated using the phonenumbers library
    """

    def __init__(self, *args, **kwargs):
        self.country = kwargs.pop("country", None)
        return super(MSISDNField, self).__init__(*args, **kwargs)

    def to_representation(self, obj):
        number = phonenumbers.parse(obj, self.country)
        return phonenumbers.format_number(number, phonenumbers.PhoneNumberFormat.E164)

    def to_internal_value(self, data):
        try:
            number = phonenumbers.parse(data, self.country)
        except phonenumbers.NumberParseException as e:
            raise serializers.ValidationError(str(e))
        if not phonenumbers.is_possible_number(number):
            raise serializers.ValidationError("Not a possible phone number")
        if not phonenumbers.is_valid_number(number):
            raise serializers.ValidationError("Not a valid phone number")
        return phonenumbers.format_number(number, phonenumbers.PhoneNumberFormat.E164)


class MSISDNSerializer(serializers.Serializer):
    msisdn = MSISDNField(country="ZA")


class Covid19TriageSerializer(BaseEventSerializer):
    msisdn = MSISDNField(country="ZA")
    deduplication_id = serializers.CharField(default=uuid.uuid4, max_length=255)

    class Meta:
        model = Covid19Triage
        fields = (
            "id",
            "deduplication_id",
            "msisdn",
            "source",
            "province",
            "city",
            "age",
            "fever",
            "cough",
            "sore_throat",
            "difficulty_breathing",
            "exposure",
            "tracing",
            "risk",
            "gender",
            "location",
            "muscle_pain",
            "smell",
            "preexisting_condition",
            "completed_timestamp",
            "timestamp",
            "created_by",
            "data",
        )
        read_only_fields = ("id", "created_by")


class Covid19TriageV2Serializer(BaseEventSerializer):
    msisdn = MSISDNField(country="ZA")
    deduplication_id = serializers.CharField(default=uuid.uuid4, max_length=255)

    class Meta:
        model = Covid19Triage
        fields = (
            "id",
            "deduplication_id",
            "msisdn",
            "first_name",
            "last_name",
            "source",
            "province",
            "city",
            "age",
            "date_of_birth",
            "fever",
            "cough",
            "sore_throat",
            "difficulty_breathing",
            "exposure",
            "confirmed_contact",
            "tracing",
            "risk",
            "gender",
            "location",
            "city_location",
            "muscle_pain",
            "smell",
            "preexisting_condition",
            "rooms_in_household",
            "persons_in_household",
            "completed_timestamp",
            "timestamp",
            "created_by",
            "data",
        )
        read_only_fields = ("id", "created_by")


class Covid19TriageV3Serializer(BaseEventSerializer):
    msisdn = MSISDNField(country="ZA")
    deduplication_id = serializers.CharField(default=uuid.uuid4, max_length=255)
    place_of_work = serializers.CharField(required=False)

    class Meta:
        model = Covid19Triage
        fields = (
            "id",
            "deduplication_id",
            "msisdn",
            "first_name",
            "last_name",
            "source",
            "province",
            "city",
            "age",
            "date_of_birth",
            "fever",
            "cough",
            "sore_throat",
            "difficulty_breathing",
            "exposure",
            "confirmed_contact",
            "tracing",
            "risk",
            "gender",
            "location",
            "city_location",
            "muscle_pain",
            "smell",
            "preexisting_condition",
            "rooms_in_household",
            "persons_in_household",
            "completed_timestamp",
            "timestamp",
            "created_by",
            "data",
            "place_of_work",
        )
        read_only_fields = ("id", "created_by")


class HealthCheckUserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = HealthCheckUserProfile
        fields = "__all__"

    def update(self, instance, validated_data):
        if "data" in validated_data:
            data = validated_data.pop("data")
            instance.data.update(data)
        super().update(instance, validated_data)
        return instance
