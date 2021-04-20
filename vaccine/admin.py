from django.contrib import admin

from userprofile.admin import BaseEventAdmin
from vaccine.models import VaccineRegistration


@admin.register(VaccineRegistration)
class VaccineRegistrationAdmin(BaseEventAdmin):
    readonly_fields = ("id", "created_by", "timestamp")
    list_display = ("msisdn", "source", "timestamp")
