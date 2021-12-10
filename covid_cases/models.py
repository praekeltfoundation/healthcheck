from __future__ import annotations

from datetime import date
from functools import lru_cache

from django.db import models
from django.db.models import Max, Sum, constraints


class Province(models.Model):
    name = models.CharField(
        max_length=50, help_text="Province name, eg. Western Cape", blank=True
    )
    created_at = models.DateTimeField(
        auto_now_add=True, help_text="When this was added to the database"
    )
    updated_at = models.DateTimeField(
        auto_now=True, help_text="When this was last updated"
    )

    def __str__(self):
        return self.name

    class Meta:
        constraints = [
            constraints.UniqueConstraint(fields=["name"], name="unique_province")
        ]

    @staticmethod
    @lru_cache(maxsize=None)
    def get_province(province: str) -> Province:
        province, _ = Province.objects.get_or_create(name=province)
        return province


class District(models.Model):
    name = models.CharField(
        max_length=50,
        help_text="District name, eg. City of Cape Town Metro",
        blank=True,
    )
    province = models.ForeignKey(
        Province,
        on_delete=models.CASCADE,
        help_text="The parent province of this district",
    )
    created_at = models.DateTimeField(
        auto_now_add=True, help_text="When this was added to the database"
    )
    updated_at = models.DateTimeField(
        auto_now=True, help_text="When this was last updated"
    )

    def __str__(self):
        return self.name

    class Meta:
        constraints = [
            constraints.UniqueConstraint(
                fields=["province", "name"], name="unique_district"
            )
        ]

    @staticmethod
    @lru_cache(maxsize=None)
    def get_district(province: str, district: str) -> District:
        province = Province.get_province(province)
        district, _ = District.objects.get_or_create(province=province, name=district)
        return district


class SubDistrict(models.Model):
    name = models.CharField(
        max_length=50, help_text="Sub District name, eg. Northerm Health sub-District"
    )
    subdistrict_id = models.PositiveIntegerField(
        help_text="The ID of this sub district", null=True
    )
    district = models.ForeignKey(
        District,
        on_delete=models.CASCADE,
        help_text="The parent district of this sub district",
        blank=True,
    )
    created_at = models.DateTimeField(
        auto_now_add=True, help_text="When this was added to the database"
    )
    updated_at = models.DateTimeField(
        auto_now=True, help_text="When this was last updated"
    )

    def __str__(self):
        return self.name

    class Meta:
        constraints = [
            constraints.UniqueConstraint(
                fields=["district", "name", "subdistrict_id"], name="unique_subdistrict"
            )
        ]

    @staticmethod
    @lru_cache(maxsize=None)
    def get_sub_district(
        province: str, district: str, sub_district: str, sub_district_id: int
    ) -> SubDistrict:
        district = District.get_district(province, district)
        sub_district, _ = SubDistrict.objects.get_or_create(
            district=district, name=sub_district, subdistrict_id=sub_district_id
        )
        return sub_district


class Ward(models.Model):
    ward_id = models.CharField(max_length=80, blank=True)
    ward_number = models.CharField(max_length=80, blank=True)
    sub_district = models.ForeignKey(
        SubDistrict,
        on_delete=models.CASCADE,
        help_text="The parent sub district of this ward",
    )
    created_at = models.DateTimeField(
        auto_now_add=True, help_text="When this was added to the database"
    )
    updated_at = models.DateTimeField(
        auto_now=True, help_text="When this was last updated"
    )

    def __str__(self):
        return self.ward_id

    class Meta:
        constraints = [
            constraints.UniqueConstraint(
                fields=["sub_district", "ward_id", "ward_number"], name="unique_ward"
            )
        ]

    @staticmethod
    def get_ward(
        province: str,
        district: str,
        sub_district: str,
        sub_district_id: int,
        ward_id: str,
        ward_number: str,
    ) -> Ward:
        sub_district = SubDistrict.get_sub_district(
            province, district, sub_district, sub_district_id
        )
        ward, _ = Ward.objects.get_or_create(
            sub_district=sub_district, ward_id=ward_id, ward_number=ward_number
        )
        return ward


class WardCase(models.Model):
    object_id = models.PositiveIntegerField(help_text="Unique ID for this entry")
    ward = models.ForeignKey(
        Ward, on_delete=models.CASCADE, help_text="Ward that this data is for"
    )
    male = models.PositiveIntegerField(help_text="Number of male cases")
    female = models.PositiveIntegerField(help_text="Number of female cases")
    unknown_gender = models.PositiveIntegerField(
        help_text="Number of cases where the gender is unknown"
    )
    age_1_10 = models.PositiveIntegerField(
        help_text="Number of cases for the 1-10 years age group"
    )
    age_11_20 = models.PositiveIntegerField(
        help_text="Number of cases for the 11-20 years age group"
    )
    age_21_30 = models.PositiveIntegerField(
        help_text="Number of cases for the 21-30 years age group"
    )
    age_31_40 = models.PositiveIntegerField(
        help_text="Number of cases for the 31-40 years age group"
    )
    age_41_50 = models.PositiveIntegerField(
        help_text="Number of cases for the 41-50 years age group"
    )
    age_51_60 = models.PositiveIntegerField(
        help_text="Number of cases for the 51-60 years age group"
    )
    age_61_70 = models.PositiveIntegerField(
        help_text="Number of cases for the 61-70 years age group"
    )
    age_71_80 = models.PositiveIntegerField(
        help_text="Number of cases for the 71-80 years age group"
    )
    age_81 = models.PositiveIntegerField(
        help_text="Number of cases for the >=81 years age group"
    )
    unknown_age = models.PositiveIntegerField(
        help_text="Number of cases where the age is unknown"
    )
    latest = models.PositiveIntegerField(help_text="Number of new cases today")
    total_number_of_cases = models.PositiveIntegerField(
        help_text="Total number of cases for this ward"
    )
    date = models.DateField(default=date.today, help_text="The day the data is for")
    created_at = models.DateTimeField(
        auto_now_add=True, help_text="When this was added to the database"
    )
    updated_at = models.DateTimeField(
        auto_now=True, help_text="When this was last updated"
    )

    class Meta:
        constraints = [
            constraints.UniqueConstraint(
                fields=["date", "object_id"], name="unique_entries"
            )
        ]

    def __str__(self):
        return self.created_at.isoformat()

    @staticmethod
    def get_database_total_cases() -> int:
        latest_date = WardCase.objects.aggregate(latest_date=Max("date"))["latest_date"]
        return (
            WardCase.objects.filter(date=latest_date).aggregate(
                total=Sum("total_number_of_cases")
            )["total"]
            or 0
        )


class SACoronavirusCounter(models.Model):
    tests = models.PositiveIntegerField(help_text="Total tests completed")
    positive = models.PositiveIntegerField(help_text="Total positive cases identified")
    recoveries = models.PositiveIntegerField(help_text="Total recoveries")
    deaths = models.PositiveIntegerField(help_text="Total deaths")
    vaccines = models.PositiveIntegerField(help_text="Total vaccines administered")
    date = models.DateField(default=date.today, help_text="The day the data is for")
    created_at = models.DateTimeField(
        auto_now_add=True, help_text="When this was added to the database"
    )
    updated_at = models.DateTimeField(
        auto_now=True, help_text="When this was last updated"
    )

    class Meta:
        constraints = [
            constraints.UniqueConstraint(fields=["date"], name="unique_counters")
        ]

    def __str__(self):
        return self.date.isoformat()
