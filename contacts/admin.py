from django import forms
from django.contrib import admin

from .models import Case, Contact


class CaseEditForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["contact"].widget.attrs.update({"style": "width: 260px"})

    fields = "__all__"


@admin.register(Case)
class CaseAdmin(admin.ModelAdmin):
    form = CaseEditForm
    list_display = (
        "id",
        "external_id",
        "date_start",
        "date_end",
        "created_at",
        "is_active",
    )

    list_filter = (
        "date_start",
        "created_at",
        "is_active",
    )
    raw_id_fields = ("contact",)


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ("msisdn",)
