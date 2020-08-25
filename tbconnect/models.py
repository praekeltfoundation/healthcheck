import uuid

import pycountry
from django.db import models

from userprofile.validators import geographic_coordinate, za_phone_number


class TBCheck(models.Model):
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

    COUGH_NO = "no"
    COUCH_YES_LT_2WEEKS = "yes_lt_2weeks"
    COUCH_YES_GT_2WEEKS = "yes_gt_2weeks"
    COUGH_CHOICES = (
        (COUGH_NO, "No"),
        (COUCH_YES_LT_2WEEKS, "Yes, less than 2 weeks"),
        (COUCH_YES_GT_2WEEKS, "Yes, more than 2 weeks"),
    )

    RISK_LOW = "low"
    RISK_MODERATE_WITHOUT_COUGH = "moderate_without_cough"
    RISK_MODERATE_WITH_COUGH = "moderate_with_cough"
    RISK_HIGH = "high"
    RISK_CHOICES = (
        (RISK_LOW, "Low"),
        (RISK_MODERATE_WITHOUT_COUGH, "Moderate without cough"),
        (RISK_MODERATE_WITH_COUGH, "Moderate with cough"),
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

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_by = models.CharField(max_length=255, blank=True, default="")
    msisdn = models.CharField(max_length=255, validators=[za_phone_number])
    source = models.CharField(max_length=255)
    province = models.CharField(max_length=6, choices=PROVINCE_CHOICES)
    city = models.CharField(max_length=255)
    age = models.CharField(max_length=5, choices=AGE_CHOICES)
    gender = models.CharField(
        max_length=7, choices=GENDER_CHOICES, blank=True, default=""
    )
    location = models.CharField(
        max_length=255, blank=True, default="", validators=[geographic_coordinate]
    )
    cough = models.CharField(max_length=13, choices=COUGH_CHOICES)
    fever = models.BooleanField()
    sweat = models.BooleanField()
    weight = models.BooleanField()
    exposure = models.CharField(max_length=9, choices=EXPOSURE_CHOICES)
    tracing = models.BooleanField(help_text="Whether the NDoH can contact the user")
