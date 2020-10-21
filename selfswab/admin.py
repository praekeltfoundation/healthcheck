from django.contrib import admin

from userprofile.admin import BaseEventAdmin

from .models import SelfSwabScreen, SelfSwabTest


@admin.register(SelfSwabScreen)
class SelfSwabScreenAdmin(BaseEventAdmin):
    readonly_fields = ("id", "contact_id", "risk_type", "timestamp")
    list_display = ("contact_id", "risk_type", "timestamp")


@admin.register(SelfSwabTest)
class SelfSwabTestAdmin(BaseEventAdmin):
    readonly_fields = ("id", "contact_id", "result", "barcode", "timestamp")
    list_display = ("contact_id", "result", "barcode", "timestamp")
