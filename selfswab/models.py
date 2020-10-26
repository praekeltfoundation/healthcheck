import uuid

from django.db import models
from django.utils import timezone

from healthcheck.utils import hash_string
from userprofile.validators import za_phone_number


class SelfSwabScreen(models.Model):
    LOW_RISK = "Low"
    HIGH_RISK = "High"
    RISK_TYPES = ((LOW_RISK, "Low"), (HIGH_RISK, "High"))

    AGE_U18 = "<18"
    AGE_18T40 = "18-39"
    AGE_40T65 = "40-65"
    AGE_O65 = ">65"
    AGE_CHOICES = (
        (AGE_U18, AGE_U18),
        (AGE_18T40, AGE_18T40),
        (AGE_40T65, AGE_40T65),
        (AGE_O65, AGE_O65),
    )

    GENDER_MALE = "Male"
    GENDER_FEMALE = "Female"
    GENDER_OTHER = "Other"
    GENDER_NOT_SAY = "not_say"
    GENDER_CHOICES = (
        (GENDER_MALE, "Male"),
        (GENDER_FEMALE, "Female"),
        (GENDER_OTHER, "Other"),
        (GENDER_NOT_SAY, "not_say"),
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

    @property
    def hashed_msisdn(self):
        return hash_string(self.msisdn)

    def get_processed_data(self):
        return {
            "id": str(self.id),
            "contact_id": self.contact_id,
            "msisdn": self.hashed_msisdn,
            "age": self.age,
            "gender": self.gender,
            "facility": self.facility,
            "risk_type": self.risk_type,
            "timestamp": self.timestamp.isoformat(),
            "occupation": self.occupation,
            "employee_number": self.employee_number,
            "pre_existing_condition": self.pre_existing_condition,
            "cough": self.cough,
            "fever": self.fever,
            "shortness_of_breath": self.shortness_of_breath,
            "body_aches": self.body_aches,
            "loss_of_taste_smell": self.loss_of_taste_smell,
            "sore_throat": self.sore_throat,
            "additional_symptoms": self.additional_symptoms,
        }


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

    @property
    def hashed_msisdn(self):
        return hash_string(self.msisdn)

    def get_processed_data(self):
        return {
            "id": str(self.id),
            "contact_id": self.contact_id,
            "msisdn": self.hashed_msisdn,
            "result": self.result,
            "barcode": self.barcode,
            "timestamp": self.timestamp.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
