import uuid
from datetime import timedelta

from django.db import models
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField

from users.models import User


class CaseQuerySet(models.QuerySet):
    def up_for_notification(self):
        return self.select_related("contact").filter(
            # GTE because cases will be checked periodically
            date_start__gte=timezone.now() + timedelta(days=14),
            # only select active cases
            is_active=True,
        )


class CaseManager(models.Manager):
    def get_queryset(self):
        return CaseQuerySet(self.model, using=self._db)

    def up_for_notification(self):
        return self.get_queryset().up_for_notification()


class Case(models.Model):
    date_start = models.DateTimeField(null=False, auto_now_add=False)
    date_notification = models.DateTimeField(null=True, auto_now_add=True)
    case_id = models.CharField(blank=True, null=True, max_length=50)
    name = models.CharField(blank=True, null=True, max_length=30)
    created_by = models.ForeignKey(
        User, related_name="cases", on_delete=models.SET_NULL, null=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    objects = CaseManager()

    @property
    def date_end(self):
        return self.date_start + timedelta(days=14)


class ContactManager(models.Manager):
    def create(self, msisdn, external_id, **args):
        contact = self.model(msisdn=msisdn)
        contact.id = external_id
        contact.save()
        return contact


class Contact(models.Model):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, db_index=True
    )
    msisdn = PhoneNumberField()
    cases = models.ManyToManyField("Case", related_name="contact")

    objects = ContactManager()

    # def save(self, *args, **kwargs):
    #     external_id = kwargs.pop("external_id", None)
    #     if external_id is not None:
    #         # override automatically created uuid with preset uuid
    #         self.pk = uuid.UUID(external_id)
    #     super().save(*args, **kwargs)
