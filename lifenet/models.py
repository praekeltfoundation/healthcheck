import uuid

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django_prometheus.models import ExportModelOperationsMixin

from healthcheck.utils import hash_string


class LNCheck(ExportModelOperationsMixin("ln-check"), models.Model):
    class Age(models.TextChoices):
        AGE_U18 = "<18", _("<18")
        AGE_18T39 = "18-39", _("18-39")
        AGE_40T65 = "40-65", _("40-65")
        AGE_O65 = ">65", _(">65")

    class Exposure(models.TextChoices):
        EXPOSURE_YES = "yes", _("Yes")
        EXPOSURE_NO = "no", _("No")
        EXPOSURE_NOT_SURE = "not_sure", _("Not Sure")

    class Risk(models.TextChoices):
        RISK_LOW = "low", _("Low")
        RISK_MODERATE = "moderate", _("Moderate")
        RISK_HIGH = "high", _("High")

    class Language(models.TextChoices):
        LANGUAGE_ENGLISH = "eng", _("English")
        LANGUAGE_FRENCH = "fr", _("Français")

    deduplication_id = models.CharField(max_length=255, default=uuid.uuid4, unique=True)
    created_by = models.CharField(max_length=255, blank=True, default="")
    msisdn = models.CharField(max_length=255, db_index=True)
    source = models.CharField(max_length=255)
    age = models.CharField(max_length=5, choices=Age.choices)
    cough = models.BooleanField()
    fever = models.BooleanField()
    sore_throat = models.BooleanField()
    difficulty_breathing = models.BooleanField()
    muscle_pain = models.BooleanField()
    smell = models.BooleanField()
    exposure = models.CharField(max_length=9, choices=Exposure.choices)
    tracing = models.BooleanField(help_text="Whether the Lifenet can contact the user")
    completed_timestamp = models.DateTimeField(default=timezone.now)
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)
    risk = models.CharField(max_length=22, choices=Risk.choices)
    follow_up_optin = models.BooleanField(default=False)
    language = models.CharField(
        max_length=3, choices=Language.choices, null=True, blank=True
    )

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
            "sore_throat": self.sore_throat,
            "difficulty_breathing": self.difficulty_breathing,
            "muscle_pain": self.muscle_pain,
            "smell": self.smell,
            "exposure": self.exposure,
            "risk": self.risk,
            "follow_up_optin": self.follow_up_optin,
            "language": self.language,
        }
