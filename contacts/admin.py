from django.contrib import admin

from .models import Case, Contact


@admin.register(Case)
class CaseAdmin(admin.ModelAdmin):
    list_display = (
        "external_id",
        "date_start",
        "date_end",
        "created_at",
    )

    list_filter = (
        "date_start",
        "created_at",
        "is_active",
    )


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ("msisdn",)
