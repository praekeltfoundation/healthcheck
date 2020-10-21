import uuid

from django.db import models
from django.utils import timezone

from userprofile.validators import za_phone_number


class SelfSwabScreen(models.Model):
    LOW_RISK = "Low"
    HIGH_RISK = "High"
    RISK_TYPES = ((LOW_RISK, "Low"), (HIGH_RISK, "High"))

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
    contact_id = models.CharField(max_length=255, blank=False)
    msisdn = models.CharField(
        max_length=255, validators=[za_phone_number], db_index=True
    )
    age = models.CharField(max_length=5, choices=AGE_CHOICES)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    facility = models.CharField(max_length=255, blank=False)
    risk_type = models.CharField(max_length=10, choices=RISK_TYPES)
    timestamp = models.DateTimeField(default=timezone.now)
    occupation = models.CharField(max_length=255, blank=True, default="")
    employee_number = models.CharField(max_length=10, blank=True, default="")
    pre_existing_condition = models.CharField(max_length=255, blank=True, default="")
    cough = models.BooleanField()
    fever = models.BooleanField()
    shortness_of_breath = models.BooleanField()
    body_aches = models.BooleanField()
    loss_of_taste_smell = models.BooleanField()
    sore_throat = models.BooleanField()
    additional_symptoms = models.BooleanField()
    timestamp = models.DateTimeField(default=timezone.now)


class SelfSwabTest(models.Model):
    RESULT_PENDING = "Pending"
    RESULT_POSITIVE = "Positive"
    RESULT_NEGATIVE = "Negative"
    RESULT_REJECTED = "Rejected"
    RESULT_EQV = "Equivocal"
    RESULT_INCONCLUSIVE = "Inconclusive"
    RESULT_INDETERMINATE = "Indeterminate"
    RESULT_INVALID = "Invalid"
    RESULT_TYPES = (
        (RESULT_PENDING, "Pending"),
        (RESULT_POSITIVE, "Positive"),
        (RESULT_NEGATIVE, "Negative"),
        (RESULT_REJECTED, "Rejected"),
        (RESULT_EQV, "Equivocal"),
        (RESULT_INCONCLUSIVE, "Inconclusive"),
        (RESULT_INDETERMINATE, "Indeterminate"),
        (RESULT_INVALID, "Invalid"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_by = models.CharField(max_length=255, blank=True, default="")
    contact_id = models.CharField(max_length=255, blank=False)
    msisdn = models.CharField(max_length=255, validators=[za_phone_number])
    result = models.CharField(
        max_length=100, choices=RESULT_TYPES, default=RESULT_PENDING
    )
    barcode = models.CharField(max_length=255, blank=False)
    timestamp = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)
