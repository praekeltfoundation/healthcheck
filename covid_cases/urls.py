from rest_framework import routers

from covid_cases.views import (
    DistrictViewSet,
    ProvinceViewSet,
    SubDistrictViewSet,
    WardCaseViewSet,
    WardViewSet,
)

v2router = routers.DefaultRouter()
v2router.register("covidcases/province", ProvinceViewSet)
v2router.register("covidcases/district", DistrictViewSet)
v2router.register("covidcases/subdistrict", SubDistrictViewSet)
v2router.register("covidcases/ward", WardViewSet)
v2router.register("covidcases/wardcase", WardCaseViewSet)