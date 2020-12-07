import uuid

from django.db import models
from django.utils import timezone

from healthcheck.utils import hash_string
from userprofile.validators import za_phone_number


class BaseModel:
    class Age(models.TextChoices):
        UNDER_18 = "<18", "<18"
        FROM_18_TO_40 = "18-39", "18-39"
        FROM_40_TO_65 = "40-65", "40-65"
        OVER_65 = ">65", ">65"

    class Gender(models.TextChoices):
        MALE = "Male", "Male"
        FEMALE = "Female", "Female"
        OTHER = "Other", "Other"
        NOT_SAY = "not_say", "not_say"


class SelfSwabRegistration(models.Model, BaseModel):
    class OptOutReason(models.TextChoices):
        REMINDERS = (
            "reminders",
            "I no longer want to receive weekly screening reminders",
        )
        TESTED_POSITIVE = (
            "tested_positive",
            "I have tested positive for COVID-19, and so can no longer be part of the study",
        )
        OTHER = "other", "Other"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_by = models.CharField(max_length=255)
    employee_number = models.CharField(max_length=255, blank=True, default="")
    contact_id = models.CharField(max_length=255, blank=True, default="")
    first_name = models.CharField(max_length=255, blank=False)
    last_name = models.CharField(max_length=255, blank=False)
    facility = models.CharField(max_length=255, blank=False)
    occupation = models.CharField(max_length=255, blank=True, default="")
    age = models.CharField(max_length=5, choices=BaseModel.Age.choices, null=True)
    gender = models.CharField(
        max_length=10, choices=BaseModel.Gender.choices, null=True
    )
    opted_out = models.BooleanField(default=False)
    optout_reason = models.CharField(
        max_length=15, choices=OptOutReason.choices, null=True
    )
    optout_timestamp = models.DateTimeField(null=True)
    timestamp = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)
    should_sync = models.BooleanField(default=True)

    @property
    def hashed_employee_number(self):
        return hash_string(self.employee_number)

    def get_processed_data(self):
        return {
            "id": str(self.id),
            "contact_id": self.contact_id,
            "employee_number": self.hashed_employee_number,
            "facility": self.facility,
            "occupation": self.occupation,
            "age": self.age,
            "gender": self.gender,
            "opted_out": self.opted_out,
            "optout_reason": self.opted_out_reason,
            "optout_timestamp": self.optout_timestamp.isoformat(),
            "timestamp": self.timestamp.isoformat(),
            "updated_at": self.timestamp.isoformat(),
        }


class SelfSwabScreen(models.Model, BaseModel):
    LOW_RISK = "Low"
    HIGH_RISK = "High"
    RISK_TYPES = ((LOW_RISK, "Low"), (HIGH_RISK, "High"))

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_by = models.CharField(max_length=255, blank=True, default="")
    contact_id = models.CharField(max_length=255, blank=False)
    msisdn = models.CharField(
        max_length=255, validators=[za_phone_number], db_index=True
    )
    age = models.CharField(max_length=5, choices=BaseModel.Age.choices)
    gender = models.CharField(max_length=10, choices=BaseModel.Gender.choices)
    facility = models.CharField(max_length=255, blank=False)
    risk_type = models.CharField(max_length=10, choices=RISK_TYPES)
    occupation = models.CharField(max_length=255, blank=True, default="")
    employee_number = models.CharField(max_length=255, blank=True, default="")
    pre_existing_condition = models.CharField(max_length=255, blank=True, default="")
    cough = models.BooleanField()
    fever = models.BooleanField()
    shortness_of_breath = models.BooleanField()
    body_aches = models.BooleanField()
    loss_of_taste_smell = models.BooleanField()
    sore_throat = models.BooleanField()
    additional_symptoms = models.BooleanField()
    should_sync = models.BooleanField(default=True)
    timestamp = models.DateTimeField(default=timezone.now)

    @property
    def hashed_msisdn(self):
        return hash_string(self.msisdn)

    @property
    def hashed_employee_number(self):
        return hash_string(self.employee_number)

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
            "employee_number": self.hashed_employee_number,
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
    RESULT_INVALID = "Invalid"
    RESULT_EQUIVOCAL = "Equivocal"
    RESULT_INCONCLUSIVE = "Inconclusive"
    RESULT_INDETERMINATE = "Indeterminate"
    RESULT_ERROR = "Error"
    RESULT_TYPES = (
        (RESULT_PENDING, "Pending"),
        (RESULT_POSITIVE, "Positive"),
        (RESULT_NEGATIVE, "Negative"),
        (RESULT_REJECTED, "Rejected"),
        (RESULT_INVALID, "Invalid"),
        (RESULT_EQUIVOCAL, "Equivocal"),
        (RESULT_INCONCLUSIVE, "Inconclusive"),
        (RESULT_INDETERMINATE, "Indeterminate"),
        (RESULT_ERROR, "Error"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_by = models.CharField(max_length=255, blank=True, default="")
    contact_id = models.CharField(max_length=255, blank=False)
    msisdn = models.CharField(max_length=255, validators=[za_phone_number])
    result = models.CharField(
        max_length=100, choices=RESULT_TYPES, default=RESULT_PENDING
    )
    barcode = models.CharField(max_length=255, blank=False, unique=True)
    timestamp = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)
    collection_timestamp = models.DateTimeField(null=True)
    received_timestamp = models.DateTimeField(null=True)
    authorized_timestamp = models.DateTimeField(null=True)
    should_sync = models.BooleanField(default=True)

    @property
    def hashed_msisdn(self):
        return hash_string(self.msisdn)

    def get_processed_data(self):
        collection_timestamp = None
        received_timestamp = None
        authorized_timestamp = None

        if self.collection_timestamp:
            collection_timestamp = self.collection_timestamp.isoformat()
        if self.received_timestamp:
            received_timestamp = self.received_timestamp.isoformat()
        if self.authorized_timestamp:
            authorized_timestamp = self.authorized_timestamp.isoformat()

        return {
            "id": str(self.id),
            "contact_id": self.contact_id,
            "msisdn": self.hashed_msisdn,
            "result": self.result,
            "barcode": self.barcode,
            "timestamp": self.timestamp.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "collection_timestamp": collection_timestamp,
            "received_timestamp": received_timestamp,
            "authorized_timestamp": authorized_timestamp,
        }

    def set_result(self, result):
        if result.upper() in ["POS", "POSITIVE", "DETECTED"]:
            self.result = SelfSwabTest.RESULT_POSITIVE
        elif result.upper() in ["NEG", "NEGATIVE", "NOT DET", "NOT DETECTED"]:
            self.result = SelfSwabTest.RESULT_NEGATIVE
        elif result.upper() in ["INV", "INVALID"]:
            self.result = SelfSwabTest.RESULT_INVALID
        elif result.upper() in ["REJECTED", "REJ"]:
            self.result = SelfSwabTest.RESULT_REJECTED
        elif result.upper() in ["EQV", "EQUIVOCAL"]:
            self.result = SelfSwabTest.RESULT_EQUIVOCAL
        elif result.upper() in ["INC", "INCON", "INCONCLUSIVE"]:
            self.result = SelfSwabTest.RESULT_INCONCLUSIVE
        elif result.upper() in ["INDETERMINATE", "IND"]:
            self.result = SelfSwabTest.RESULT_INDETERMINATE
        else:
            self.result = SelfSwabTest.RESULT_ERROR
