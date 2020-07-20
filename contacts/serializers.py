import uuid

from django.utils.translation import ugettext as _
from rest_framework import serializers, validators

from .exceptions import CustomBadRequest
from .models import Case, Contact


class ContactSerializer(serializers.ModelSerializer):
    external_id = serializers.UUIDField(write_only=True, required=True)

    def validate(self, attrs):
        # TODO: validate uniquity of provided uuid
        return super(ContactSerializer, self).validate(attrs)

    def create(self, validated_data):
        contact = Contact.objects.create(**validated_data)
        return contact

    class Meta:
        model = Contact
        fields = (
            "external_id",
            "id",
            "msisdn",
        )
        read_only_fields = ("id",)


class CaseSerializer(serializers.ModelSerializer):
    timestamp = serializers.DateTimeField(source="date_start")
    created_by = serializers.SerializerMethodField()

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
            "is_active",
        )
        read_only_fields = (
            "created_at",
            "created_by",
            "date_start",
            "is_active",
        )
