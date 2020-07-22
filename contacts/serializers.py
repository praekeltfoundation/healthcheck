from datetime import timedelta

from django.utils import timezone
from rest_framework import serializers

from .exceptions import CustomBadRequest
from .models import Case, Contact


class ContactSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        contact = Contact.objects.create(**validated_data)
        return contact

    class Meta:
        model = Contact
        fields = (
            "id",
            "msisdn",
        )
        read_only_fields = ("id",)


class CaseSerializer(serializers.ModelSerializer):
    timestamp = serializers.DateTimeField(source="date_start", write_only=True)
    created_by = serializers.SerializerMethodField()

    def validate(self, data):
        if data.get("date_start") > timezone.now():
            raise CustomBadRequest("Can not register future contact.")
        if data.get("date_start") + timedelta(days=14) < timezone.now():
            raise CustomBadRequest("Case expired.")
        return super(CaseSerializer, self).validate(data)

    def get_created_by(self, obj):
        return obj.created_by.username

    class Meta:
        model = Case
        fields = (
            "date_start",
            "case_id",
            "timestamp",
            "name",
            "created_by",
            "created_at",
            "external_id",
        )
        read_only_fields = (
            "created_at",
            "created_by",
            "date_start",
            "is_active",
        )
