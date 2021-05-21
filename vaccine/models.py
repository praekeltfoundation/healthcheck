import uuid
from django.db import models
from django.utils import timezone
from django_prometheus.models import ExportModelOperationsMixin
from userprofile.validators import za_phone_number


class VaccineRegistration(
    ExportModelOperationsMixin("vaccineregistration"), models.Model
):
    GENDER_MALE = "Male"
    GENDER_FEMALE = "Female"
    GENDER_OTHER = "Other"
    GENDER_CHOICES = (
        (GENDER_MALE, "Male"),
        (GENDER_FEMALE, "Female"),
        (GENDER_OTHER, "Other"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    deduplication_id = models.CharField(max_length=255, default=uuid.uuid4, unique=True)
    msisdn = models.CharField(max_length=255, validators=[za_phone_number])
    source = models.CharField(max_length=255)
    gender = models.CharField(
        max_length=7, choices=GENDER_CHOICES, blank=True, default=""
    )
    first_name = models.CharField(max_length=255, blank=True, null=True, default=None)
    last_name = models.CharField(max_length=255, blank=True, null=True, default=None)
    date_of_birth = models.DateField(blank=True, null=True, default=None)
    preferred_time = models.CharField(
        max_length=255, blank=True, null=True, default=None
    )
    preferred_date = models.CharField(
        max_length=255, blank=True, null=True, default=None
    )
    preferred_location_id = models.CharField(max_length=255)
    preferred_location_name = models.CharField(max_length=255)
    id_number = models.CharField(max_length=255, blank=True, default="")
    refugee_number = models.CharField(
        max_length=255, blank=True, null=True, default=None
    )
    asylum_seeker_number = models.CharField(
        max_length=255, blank=True, null=True, default=None
    )
    passport_number = models.CharField(
        max_length=255, blank=True, null=True, default=None
    )
    passport_country = models.CharField(
        max_length=255, blank=True, null=True, default=None
    )
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)
    created_by = models.CharField(max_length=255, blank=True, default="")
    data = models.JSONField(default=dict, blank=True, null=True)


class VaccineSuburb(models.Model):
    province = models.CharField(max_length=255)
    municipality = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    suburb = models.CharField(max_length=255)
    suburb_id = models.CharField(max_length=255)
