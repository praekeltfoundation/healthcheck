from django.contrib import admin

from userprofile.admin import BaseEventAdmin

from .models import LNCheck, LNTest


@admin.register(LNCheck)
class LifenetCheckAdmin(BaseEventAdmin):
    readonly_fields = ("id", "created_by", "timestamp")
    list_display = ("msisdn", "risk", "source", "timestamp")
