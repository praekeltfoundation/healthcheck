import uuid
from datetime import timedelta

from django.conf import settings
from django.db import models
from django.db.models import ExpressionWrapper, F, fields
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField

from users.models import User


def get_uuid():
    return uuid.uuid4().hex


class Contact(models.Model):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, db_index=True
    )
    msisdn = PhoneNumberField(unique=True)


class CaseQuerySet(models.QuerySet):
    def up_for_notification(self):
        return self.select_related("contact").filter(
            # exclude ones where notification has been already set
            date_notification_end=None,
            # LTE because cases will be checked periodically
            # and some of them might be missed in one of the checks
            # GTE would select future cases which is not indended behaviour
            contact_date_end__lte=timezone.now(),
            # only select active cases
            is_active=True,
        )


class CaseManager(models.Manager):
    def create(self, **kwargs):
        contact = self.model(**kwargs)
        contact.save()
        return contact

    def get_queryset(self):
        return CaseQuerySet(self.model, using=self._db)

    def with_end_date(self):
        date_end_expression = ExpressionWrapper(
            expression=F("date_start") + timedelta(days=settings.TIMEFRAME),
            output_field=fields.DateTimeField(),
        )
        return self.annotate(contact_date_end=date_end_expression)

    def up_for_notification(self):
        return self.get_queryset().up_for_notification()


class Case(models.Model):
    external_id = models.CharField(
        max_length=255, blank=False, default=get_uuid, unique=True,
    )
    date_start = models.DateTimeField(null=False, auto_now_add=False)
    date_notification_start = models.DateTimeField(null=True, auto_now_add=False)
    date_notification_end = models.DateTimeField(null=True, auto_now_add=False)
    case_id = models.CharField(blank=True, null=True, max_length=50)
    name = models.CharField(blank=True, null=True, max_length=30)
    created_by = models.ForeignKey(
        User, related_name="cases", on_delete=models.SET_NULL, null=True,
    )
    contact = models.ForeignKey(
        Contact, null=True, related_name="cases", on_delete=models.SET_NULL,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    objects = CaseManager()

    @property
    def date_end(self):
        return self.date_start + timedelta(days=settings.TIMEFRAME)
