from django.contrib import admin

from userprofile.admin import BaseEventAdmin
from vaccine.models import VaccineRegistration, VaccineSuburb
from import_export.admin import ImportExportActionModelAdmin
from import_export import resources


@admin.register(VaccineRegistration)
class VaccineRegistrationAdmin(BaseEventAdmin):
    readonly_fields = ("id", "created_by", "timestamp")
    list_display = ("msisdn", "source", "timestamp")
    list_filter = ["timestamp"]


class SuburbResource(resources.ModelResource):
    class Meta:
        model = VaccineSuburb
        import_id_fields = ("suburb_id",)
        fields = ("province", "municipality", "city", "suburb", "suburb_id")


@admin.register(VaccineSuburb)
class VaccineSuburbAdmin(ImportExportActionModelAdmin, admin.ModelAdmin):
    resource_class = SuburbResource
    list_display = ["province", "municipality", "city", "suburb", "suburb_id"]
    list_filter = ["province"]
    search_fields = ["province", "municipality", "city", "suburb"]
