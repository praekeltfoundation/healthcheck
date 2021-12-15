from rest_framework import serializers
from real411.models import Complaint


class ComplaintSerializer(serializers.ModelSerializer):
    class Meta:
        model = Complaint
        fields = ["id", "complaint_ref", "msisdn", "created_at", "updated_at"]
