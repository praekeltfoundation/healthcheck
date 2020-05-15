from django.db import models
from django.utils import timezone

from confirmed_contact.validators import za_phone_number


class ConfirmedContact(models.Model):
    external_id = models.CharField(
        max_length=255,
        unique=True,
        blank=True,
        null=True,
        default=None,
        help_text="The ID of this entry on the external system. Used for deduplication",
    )
    msisdn = models.CharField(
        max_length=255,
        help_text="MSISDN of the confirmed contact",
        validators=(za_phone_number,),
    )
    timestamp = models.DateTimeField(
        default=timezone.now,
        blank=True,
        help_text="Timestamp of when contact was confirmed",
    )
    set_active = models.BooleanField(
        default=False,
        blank=True,
        editable=False,
        help_text="Whether the contact has been set to active in Turn",
    )
    set_inactive = models.BooleanField(
        default=False,
        blank=True,
        editable=False,
        help_text="Whether the contact has been set to inactive in Turn",
    )
    name = models.CharField(
        max_length=255,
        default="",
        blank=True,
        help_text="Name of the confirmed contact",
    )
    case_id = models.CharField(
        max_length=255, default="", blank=True, help_text="Case ID of the confirmation"
    )
    created_by = models.CharField(
        max_length=255, help_text="Django username who created this"
    )
    created_at = models.DateTimeField(
        auto_now_add=True, help_text="When this was added to the database"
    )

    class Meta:
        indexes = [
            # To check if we're processing the latest record for this msisdn
            models.Index(fields=("msisdn", "-timestamp")),
            # To get all the entries that we need to set active
            models.Index(
                fields=("set_active",),
                condition=models.Q(set_active=False),
                name="active_false_idx",
            ),
            # To get all the entries that we need to set inactive
            models.Index(
                fields=("set_inactive", "timestamp"),
                condition=models.Q(set_inactive=False),
                name="inactive_false_idx",
            ),
        ]
