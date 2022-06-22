from django.urls import path

from .views import ClinicFinderView

app_name = "clinicfinder"

urlpatterns = [
    path("clinic_finder/", ClinicFinderView.as_view(), name="clinic_finder",),
]
