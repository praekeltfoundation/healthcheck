import uuid

from django.db import models
from django.utils import timezone
from django_prometheus.models import ExportModelOperationsMixin

from healthcheck.utils import hash_string


class LNCheck(ExportModelOperationsMixin("ln-check"), models.Model):
    AGE_U18 = "<18"
    AGE_18T39 = "18-39"
    AGE_40T65 = "40-65"
    AGE_O65 = ">65"
    AGE_CHOICES = (
        (AGE_U18, AGE_U18),
        (AGE_18T39, AGE_18T39),
        (AGE_40T65, AGE_40T65),
        (AGE_O65, AGE_O65),
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

    deduplication_id = models.CharField(max_length=255, default=uuid.uuid4, unique=True)
    created_by = models.CharField(max_length=255, blank=True, default="")
    msisdn = models.CharField(max_length=255, db_index=True)
    source = models.CharField(max_length=255)
    age = models.CharField(max_length=5, choices=AGE_CHOICES)
    cough = models.BooleanField()
    fever = models.BooleanField()
    sore_throat = models.BooleanField()
    difficulty_breathing = models.BooleanField()
    muscle_pain = models.BooleanField()
    smell = models.BooleanField()
    exposure = models.CharField(max_length=9, choices=EXPOSURE_CHOICES)
    tracing = models.BooleanField(help_text="Whether the Lifenet can contact the user")
    completed_timestamp = models.DateTimeField(default=timezone.now)
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)
    risk = models.CharField(max_length=22, choices=RISK_CHOICES)
    follow_up_optin = models.BooleanField(default=False)

    @property
    def hashed_msisdn(self):
        return hash_string(self.msisdn)

    def get_processed_data(self):
        return {
            "deduplication_id": str(self.deduplication_id),
            "msisdn": self.hashed_msisdn,
            "timestamp": self.timestamp.isoformat(),
            "source": self.source,
            "age": self.age,
            "cough": self.cough,
            "fever": self.fever,
            "sore_throat": self.sweat,
            "difficulty_breathing": self.weight,
            "muscle_pain": self.muscle_pain,
            "smell": self.smell,
            "exposure": self.exposure,
            "risk": self.risk,
            "follow_up_optin": self.follow_up_optin,
            "language": self.language,
        }
