from rest_framework import serializers

from covid_cases.models import (
    District,
    Province,
    SACoronavirusCounter,
    SubDistrict,
    Ward,
    WardCase,
)


class ProvinceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Province
        fields = ["id", "name", "created_at", "updated_at"]


class DistrictSerializer(serializers.ModelSerializer):
    class Meta:
        model = District
        fields = ["id", "name", "province", "created_at", "updated_at"]


class SubDistrictSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubDistrict
        fields = [
            "id",
            "name",
            "subdistrict_id",
            "district",
            "created_at",
            "updated_at",
        ]


class WardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ward
        fields = [
            "id",
            "ward_id",
            "ward_number",
            "sub_district",
            "created_at",
            "updated_at",
        ]


class WardCaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = WardCase
        fields = [
            "id",
            "ward",
            "male",
            "female",
            "unknown_gender",
            "age_1_10",
            "age_11_20",
            "age_21_30",
            "age_31_40",
            "age_41_50",
            "age_51_60",
            "age_61_70",
            "age_71_80",
            "age_81",
            "unknown_age",
            "latest",
            "total_number_of_cases",
            "created_at",
            "updated_at",
        ]


class WardCaseFlatSerializer(serializers.ModelSerializer):
    ward_id = serializers.CharField(source="ward.ward_id")
    ward_number = serializers.CharField(source="ward.ward_number")
    subdistrict = serializers.CharField(source="ward.sub_district.name")
    subdistrict_id = serializers.IntegerField(source="ward.sub_district.subdistrict_id")
    district = serializers.CharField(source="ward.sub_district.district.name")
    province = serializers.CharField(source="ward.sub_district.district.province.name")

    class Meta:
        model = WardCase
        fields = [
            "id",
            "object_id",
            "ward_id",
            "ward_number",
            "subdistrict",
            "subdistrict_id",
            "district",
            "province",
            "male",
            "female",
            "unknown_gender",
            "age_1_10",
            "age_11_20",
            "age_21_30",
            "age_31_40",
            "age_41_50",
            "age_51_60",
            "age_61_70",
            "age_71_80",
            "age_81",
            "unknown_age",
            "latest",
            "total_number_of_cases",
            "date",
            "created_at",
            "updated_at",
        ]


class SACoronavirusCounterSerializer(serializers.ModelSerializer):
    class Meta:
        model = SACoronavirusCounter
        fields = [
            "id",
            "tests",
            "positive",
            "recoveries",
            "deaths",
            "vaccines",
            "date",
            "created_at",
            "updated_at",
        ]
