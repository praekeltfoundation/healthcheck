from django.contrib import admin

from userprofile.admin import BaseEventAdmin

from .models import SelfSwabRegistration, SelfSwabScreen, SelfSwabTest


@admin.register(SelfSwabScreen)
class SelfSwabScreenAdmin(BaseEventAdmin):
    readonly_fields = ("id", "contact_id", "risk_type", "timestamp")
    list_display = ("contact_id", "risk_type", "timestamp")


@admin.register(SelfSwabTest)
class SelfSwabTestAdmin(BaseEventAdmin):
    readonly_fields = ("id", "contact_id", "result", "barcode", "timestamp")
    list_display = ("contact_id", "result", "barcode", "timestamp")


@admin.register(SelfSwabRegistration)
class SelfSwabRegistrationAdmin(BaseEventAdmin):
    readonly_fields = ("id", "contact_id", "created_by")
    list_display = ("contact_id", "employee_number")
