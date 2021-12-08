from django.contrib import admin

from covid_cases.models import (
    Province,
    District,
    SubDistrict,
    Ward,
    WardCase,
)


@admin.register(Province)
class ProvinceAdmin(admin.ModelAdmin):
    pass


@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    pass


@admin.register(SubDistrict)
class SubDistrictAdmin(admin.ModelAdmin):
    pass


@admin.register(Ward)
class WardAdmin(admin.ModelAdmin):
    pass


@admin.register(WardCase)
class WardCaseAdmin(admin.ModelAdmin):
    pass
