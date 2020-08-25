from django.contrib import admin

from userprofile.admin import BaseEventAdmin

from .models import TBCheck


@admin.register(TBCheck)
class TBCheckAdmin(BaseEventAdmin):
    readonly_fields = ("id", "created_by", "timestamp")
    list_display = ("msisdn", "risk", "source", "timestamp")
