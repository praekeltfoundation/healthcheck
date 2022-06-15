from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from rest_framework.test import APITestCase
from django.test import override_settings


class ClinicFinderViewTests(APITestCase):
    url = reverse("clinicfinder:clinic_finder")
    fixtures = ["clinicfinder/fixtures/eastern_cape.json"]

    @override_settings(LOCATION_SEARCH_RADIUS=100)
    def test_clinic_finder_list(self):
        """
            Returns a list of the nearest clinics
        """
        user = get_user_model().objects.create_user("test")
        user.user_permissions.add(Permission.objects.get(codename="add_covid19triage"))
        self.client.force_authenticate(user)
        response = self.client.get(
            self.url, {"longitude": "25.69077", "latitude": "-33.5422"}
        )

        self.assertEqual(len(response.json().get("locations")), 5)

    def test_clinic_finder_error(self):
        """
            Returns an error if longitude or latitude is not provided
        """
        user = get_user_model().objects.create_user("test")
        user.user_permissions.add(Permission.objects.get(codename="add_covid19triage"))
        self.client.force_authenticate(user)
        response = self.client.get(self.url, {"latitude": "-33.5422"})

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json().get("error"), "longitude and latitude are required"
        )
