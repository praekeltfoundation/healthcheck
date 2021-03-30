from django.urls import path
from rest_framework import routers

from selfswab.views import (
    SelfSwabRegistrationViewSet,
    SelfSwabScreenViewSet,
    SelfSwabTestViewSet,
    WhitelistContactView,
    SendTestResultPDFView,
)

app_name = "selfswab"

v2router = routers.DefaultRouter()
v2router.register("selfswabscreen", SelfSwabScreenViewSet)
v2router.register("selfswabtest", SelfSwabTestViewSet)
v2router.register("selfswabregistration", SelfSwabRegistrationViewSet)

urlpatterns = [
    path(
        "whitelist_contact/",
        WhitelistContactView.as_view(),
        name="rest_whitelist_contact",
    ),
    path(
        "send_test_result_pdf/",
        SendTestResultPDFView.as_view(),
        name="rest_send_test_result_pdf",
    ),
]
