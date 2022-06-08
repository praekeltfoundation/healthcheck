import uuid

import pycountry
from django.db import models
from django.utils import timezone
from django_prometheus.models import ExportModelOperationsMixin

from healthcheck.utils import hash_string, extract_reduced_accuracy_lat_long
from userprofile.validators import geographic_coordinate, za_phone_number


class TBCheck(ExportModelOperationsMixin("tb-check"), models.Model):
    AGE_U18 = "<18"
    AGE_18T40 = "18-40"
    AGE_40T65 = "40-65"
    AGE_O65 = ">65"
    AGE_CHOICES = (
        (AGE_U18, AGE_U18),
        (AGE_18T40, AGE_18T40),
        (AGE_40T65, AGE_40T65),
        (AGE_O65, AGE_O65),
    )

    PROVINCE_CHOICES = sorted(
        (s.code, s.name) for s in pycountry.subdivisions.get(country_code="ZA")
    )

    EXPOSURE_YES = "yes"
    EXPOSURE_NO = "no"
    EXPOSURE_NOT_SURE = "not_sure"
    EXPOSURE_CHOICES = (
        (EXPOSURE_YES, "Yes"),
        (EXPOSURE_NO, "No"),
        (EXPOSURE_NOT_SURE, "Not sure"),
    )

    RISK_LOW = "low"
    RISK_MODERATE = "moderate"
    RISK_HIGH = "high"
    RISK_CHOICES = (
        (RISK_LOW, "Low"),
        (RISK_MODERATE, "Moderate"),
        (RISK_HIGH, "High"),
    )

    GENDER_MALE = "male"
    GENDER_FEMALE = "female"
    GENDER_OTHER = "other"
    GENDER_NOT_SAY = "not_say"
    GENDER_CHOICES = (
        (GENDER_MALE, "Male"),
        (GENDER_FEMALE, "Female"),
        (GENDER_OTHER, "Other"),
        (GENDER_NOT_SAY, "Rather not say"),
    )

    LANGUAGE_ENGLISH = "eng"
    LANGUAGE_ZULU = "zul"
    LANGUAGE_AFRIKAANS = "afr"
    LANGUAGE_XHOSA = "xho"
    LANGUAGE_SESOTHO = "sot"
    LANGUAGE_CHOICES = (
        (LANGUAGE_ENGLISH, "English"),
        (LANGUAGE_ZULU, "isiZulu"),
        (LANGUAGE_AFRIKAANS, "Afrikaans"),
        (LANGUAGE_XHOSA, "isiXhosa"),
        (LANGUAGE_SESOTHO, "Sesotho"),
    )

    COMMIT_YES = "yes"
    COMMIT_NO = "no"
    COMMIT_CHOICES = (
        (COMMIT_YES, "Yes"),
        (COMMIT_NO, "No"),
    )

    deduplication_id = models.CharField(max_length=255, default=uuid.uuid4, unique=True)
    created_by = models.CharField(max_length=255, blank=True, default="")
    msisdn = models.CharField(
        max_length=255, validators=[za_phone_number], db_index=True
    )
    source = models.CharField(max_length=255)
    province = models.CharField(max_length=6, choices=PROVINCE_CHOICES)
    city = models.CharField(max_length=255)
    age = models.CharField(max_length=5, choices=AGE_CHOICES)
    gender = models.CharField(max_length=7, choices=GENDER_CHOICES)
    location = models.CharField(
        max_length=255, validators=[geographic_coordinate], null=True
    )
    city_location = models.CharField(
        max_length=255, validators=[geographic_coordinate], null=True
    )
    cough = models.BooleanField()
    fever = models.BooleanField()
    sweat = models.BooleanField()
    weight = models.BooleanField()
    exposure = models.CharField(max_length=9, choices=EXPOSURE_CHOICES)
    tracing = models.BooleanField(help_text="Whether the NDoH can contact the user")
    completed_timestamp = models.DateTimeField(default=timezone.now)
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)
    risk = models.CharField(max_length=22, choices=RISK_CHOICES)
    follow_up_optin = models.BooleanField(default=False)
    language = models.CharField(
        max_length=3, choices=LANGUAGE_CHOICES, null=True, blank=True
    )
    data = models.JSONField(default=dict, blank=True, null=True)
    commit_get_tested = models.CharField(
        max_length=3, choices=COMMIT_CHOICES, null=True, blank=True
    )
    research_consent = models.BooleanField(null=True)
    originating_msisdn = models.CharField(
        max_length=255, validators=[za_phone_number], null=True
    )
    activation = models.CharField(max_length=255, null=True)

    @property
    def hashed_msisdn(self):
        return hash_string(self.msisdn)

    def get_processed_data(self):
        location_lat, location_long = extract_reduced_accuracy_lat_long(
            self.location, 2
        )
        city_lat, city_long = extract_reduced_accuracy_lat_long(self.city_location, 2)

        return {
            "deduplication_id": str(self.deduplication_id),
            "msisdn": self.hashed_msisdn,
            "timestamp": self.timestamp.isoformat(),
            "source": self.source,
            "province": self.province,
            "age": self.age,
            "gender": self.gender,
            "location_latitude": location_lat,
            "location_longitude": location_long,
            "city_latitude": city_lat,
            "city_longitude": city_long,
            "cough": self.cough,
            "fever": self.fever,
            "sweat": self.sweat,
            "weight": self.weight,
            "exposure": self.exposure,
            "risk": self.risk,
            "follow_up_optin": self.follow_up_optin,
            "language": self.language,
            "activation": self.activation,
            "originating_msisdn": self.originating_msisdn,
        }


class TBTest(ExportModelOperationsMixin("tb-test"), models.Model):
    RESULT_POSITIVE = "positive"
    RESULT_NEGATIVE = "negative"
    RESULT_PENDING = "pending"
    RESULT_CHOICES = (
        (RESULT_POSITIVE, "Positive"),
        (RESULT_NEGATIVE, "Negative"),
        (RESULT_PENDING, "Pending"),
    )

    deduplication_id = models.CharField(max_length=255, default=uuid.uuid4, unique=True)
    created_by = models.CharField(max_length=255, blank=True, default="")
    msisdn = models.CharField(max_length=255, validators=[za_phone_number])
    source = models.CharField(max_length=255)
    result = models.CharField(max_length=10, choices=RESULT_CHOICES)
    timestamp = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)

    @property
    def hashed_msisdn(self):
        return hash_string(self.msisdn)

    def get_processed_data(self):
        return {
            "deduplication_id": str(self.deduplication_id),
            "msisdn": self.hashed_msisdn,
            "source": self.source,
            "result": self.result,
            "timestamp": self.timestamp.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
