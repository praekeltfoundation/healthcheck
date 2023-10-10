import random
import uuid
from datetime import datetime
from typing import Text

import pycountry
from django.conf import settings
from django.contrib.postgres.indexes import GinIndex
from django.db import models
from django.utils import timezone
from django_prometheus.models import ExportModelOperationsMixin

from tbconnect.models import TBCheck
from userprofile.utils import has_value
from userprofile.validators import geographic_coordinate, za_phone_number


class Covid19Triage(ExportModelOperationsMixin("covid19triage"), models.Model):
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
    RISK_CRITICAL = "critical"
    RISK_CHOICES = (
        (RISK_LOW, "Low"),
        (RISK_MODERATE, "Moderate"),
        (RISK_HIGH, "High"),
        (RISK_CRITICAL, "Critical"),
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

    WORK_HEALTHCARE = "healthcare"
    WORK_EDUCATION = "education"
    WORK_PORT = "port_of_entry"
    WORK_OTHER = "other"

    WORK_CHOICES = (
        (WORK_HEALTHCARE, "Healthcare"),
        (WORK_EDUCATION, "Education"),
        (WORK_PORT, "Port of entry"),
        (WORK_OTHER, "Other"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    deduplication_id = models.CharField(max_length=255, default=uuid.uuid4, unique=True)
    msisdn = models.CharField(max_length=255, validators=[za_phone_number])
    first_name = models.CharField(max_length=255, blank=True, null=True, default=None)
    last_name = models.CharField(max_length=255, blank=True, null=True, default=None)
    source = models.CharField(max_length=255)
    province = models.CharField(max_length=6, choices=PROVINCE_CHOICES)
    city = models.CharField(max_length=255)
    age = models.CharField(max_length=5, choices=AGE_CHOICES)
    date_of_birth = models.DateField(blank=True, null=True, default=None)
    place_of_work = models.CharField(
        max_length=13, blank=True, null=True, default=None, choices=WORK_CHOICES
    )
    fever = models.BooleanField()
    cough = models.BooleanField()
    sore_throat = models.BooleanField()
    difficulty_breathing = models.BooleanField(null=True, blank=True, default=None)
    exposure = models.CharField(max_length=9, choices=EXPOSURE_CHOICES)
    confirmed_contact = models.BooleanField(blank=True, null=True, default=None)
    tracing = models.BooleanField(help_text="Whether the NDoH can contact the user")
    risk = models.CharField(max_length=8, choices=RISK_CHOICES)
    gender = models.CharField(
        max_length=7, choices=GENDER_CHOICES, blank=True, default=""
    )
    location = models.CharField(
        max_length=255, blank=True, default="", validators=[geographic_coordinate]
    )
    city_location = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        default=None,
        validators=[geographic_coordinate],
    )
    muscle_pain = models.BooleanField(null=True, blank=True, default=None)
    smell = models.BooleanField(null=True, blank=True, default=None)
    preexisting_condition = models.CharField(
        max_length=9, choices=EXPOSURE_CHOICES, blank=True, default=""
    )
    rooms_in_household = models.IntegerField(blank=True, null=True, default=None)
    persons_in_household = models.IntegerField(blank=True, null=True, default=None)
    completed_timestamp = models.DateTimeField(default=timezone.now)
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)
    created_by = models.CharField(max_length=255, blank=True, default="")
    data = models.JSONField(default=dict, blank=True, null=True)

    class Meta:
        db_table = "eventstore_covid19triage"
        indexes = [models.Index(fields=["msisdn", "timestamp"])]


class HealthCheckUserProfileManager(models.Manager):
    def get_or_prefill(self, msisdn: Text) -> "HealthCheckUserProfile":
        """
        Either gets the existing user profile, or creates one using data in the
        historical healthchecks
        """
        try:
            return self.get(msisdn=msisdn)
        except self.model.DoesNotExist:
            healthchecks = Covid19Triage.objects.filter(msisdn=msisdn).order_by(
                "completed_timestamp"
            )
            profile = self.model()
            for healthcheck in healthchecks.iterator():
                profile.update_from_healthcheck(healthcheck)
            return profile


class HealthCheckUserProfile(
    ExportModelOperationsMixin("healthcheck-user-profile"), models.Model
):
    ARM_CONTROL = "control"
    ARM_SOFT_COMMITMENT_PLUS = "soft_commitment_plus"
    GROUP_ARM_CHOICES = (
        (ARM_CONTROL, "Control"),
        (ARM_SOFT_COMMITMENT_PLUS, "Soft Commitment Plus"),
    )

    msisdn = models.CharField(
        primary_key=True, max_length=255, validators=[za_phone_number]
    )
    first_name = models.CharField(max_length=255, blank=True, null=True, default=None)
    last_name = models.CharField(max_length=255, blank=True, null=True, default=None)
    province = models.CharField(
        max_length=6,
        choices=Covid19Triage.PROVINCE_CHOICES,
        blank=True,
        null=True,
        default="",
    )
    city = models.CharField(max_length=255)
    age = models.CharField(max_length=5, choices=Covid19Triage.AGE_CHOICES)
    date_of_birth = models.DateField(blank=True, null=True, default=None)
    gender = models.CharField(
        max_length=7, choices=Covid19Triage.GENDER_CHOICES, blank=True, default=""
    )
    location = models.CharField(
        max_length=255, blank=True, default="", validators=[geographic_coordinate]
    )
    city_location = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        default=None,
        validators=[geographic_coordinate],
    )
    preexisting_condition = models.CharField(
        max_length=9, choices=Covid19Triage.EXPOSURE_CHOICES, blank=True, default=""
    )
    rooms_in_household = models.IntegerField(blank=True, null=True, default=None)
    persons_in_household = models.IntegerField(blank=True, null=True, default=None)
    language = models.CharField(max_length=3, null=True, blank=True)
    data = models.JSONField(default=dict, blank=True, null=True)
    tbconnect_group_arm = models.CharField(
        max_length=22, choices=GROUP_ARM_CHOICES, null=True, blank=True
    )
    tbconnect_group_arm_timestamp = models.DateTimeField(null=True)
    research_consent = models.BooleanField(null=True)
    originating_msisdn = models.CharField(
        max_length=255, validators=[za_phone_number], null=True
    )
    activation = models.CharField(max_length=255, null=True)

    objects = HealthCheckUserProfileManager()

    def update_from_healthcheck(self, healthcheck: Covid19Triage) -> None:
        """
        Updates the profile with the data from the latest healthcheck
        """

        for field in [
            "msisdn",
            "first_name",
            "last_name",
            "province",
            "city",
            "age",
            "date_of_birth",
            "gender",
            "location",
            "city_location",
            "preexisting_condition",
            "rooms_in_household",
            "persons_in_household",
        ]:
            value = getattr(healthcheck, field, None)
            if has_value(value):
                setattr(self, field, value)

        for k, v in healthcheck.data.items():
            if has_value(v):
                self.data[k] = v

    def update_from_tbcheck(self, tbcheck: TBCheck) -> None:
        """
        Updates the profile with the data from the latest TB Check
        """

        for field in [
            "msisdn",
            "province",
            "city",
            "age",
            "gender",
            "location",
            "city_location",
            "language",
            "research_consent",
            "originating_msisdn",
            "activation",
        ]:
            value = getattr(tbcheck, field, None)
            if has_value(value):
                setattr(self, field, value)

        self.data["follow_up_optin"] = tbcheck.follow_up_optin
        self.data["synced_to_tb_rapidpro"] = False

        for k, v in tbcheck.data.items():
            if has_value(v):
                self.data[k] = v

    def _get_tb_study_arms(self):
        # we can update the setting to 0 to disable this expensive check
        if self.activation == "tb_study_c":
            if settings.SOFT_COMMITMENT_PLUS_LIMIT > 0:
                soft_commitment_plus_count = HealthCheckUserProfile.objects.filter(
                    activation="tb_study_c",
                    research_consent=True,
                    tbconnect_group_arm="soft_commitment_plus",
                ).count()

                if soft_commitment_plus_count >= settings.SOFT_COMMITMENT_PLUS_LIMIT:
                    return self.GROUP_ARM_CHOICES[:1]
            elif settings.SOFT_COMMITMENT_PLUS_LIMIT == 0:
                return self.GROUP_ARM_CHOICES[:1]
        return self.GROUP_ARM_CHOICES

    def update_tbconnect_group_arm(self):
        if (
            self.activation == "tb_study_b"
            or self.activation == "tb_study_c"
            and not self.tbconnect_group_arm
            and self.research_consent
        ):
            arms = self._get_tb_study_arms()
            self.tbconnect_group_arm = random.choice(arms)[0]
            self.tbconnect_group_arm_timestamp = datetime.now()

    class Meta:
        db_table = "eventstore_healthcheckuserprofile"
        indexes = [GinIndex(fields=["data"], name="userprofile__data__gin_idx")]
