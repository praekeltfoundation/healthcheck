from django.db import models
from django.db.models import constraints
from userprofile.validators import za_phone_number


class Complaint(models.Model):
    complaint_ref = models.CharField(
        max_length=255,
        unique=True,
        help_text="The reference code for the Real411 complaint",
    )
    msisdn = models.CharField(
        max_length=255,
        validators=[za_phone_number],
        help_text="The phone number of the person who submitted the complaint",
    )
    created_at = models.DateTimeField(
        auto_now_add=True, help_text="When this complaint was created"
    )
    updated_at = models.DateTimeField(
        auto_now=True, help_text="When this complaint was last updated", db_index=True
    )
