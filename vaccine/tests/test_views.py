from urllib.parse import urlencode
from django.utils import timezone

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from vaccine.models import VaccineRegistration
from userprofile.tests.test_views import BaseEventTestCase


class VaccineRegistrationViewSetTests(APITestCase, BaseEventTestCase):
    url = reverse("vaccineregistration-list")

    def test_data_validation(self):
        """
        The supplied data must be validated, and any errors returned
        """
        user = get_user_model().objects.create_user("test")
        user.user_permissions.add(
            Permission.objects.get(codename="add_vaccineregistration")
        )
        self.client.force_authenticate(user)
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_successful_request(self):
        """
        Should create a new VaccineRegistration object in the database
        """
        now = timezone.now()
        user = get_user_model().objects.create_user("test")
        user.user_permissions.add(
            Permission.objects.get(codename="add_vaccineregistration")
        )
        self.client.force_authenticate(user)
        response = self.client.post(
            self.url,
            {
                "msisdn": "27820001001",
                "source": "USSD",
                "gender": VaccineRegistration.GENDER_MALE,
                "first_name": "Test",
                "last_name": "Testing",
                "date_of_birth": now.strftime("%Y-%m-%d"),
                "preferred_time": "morning",
                "preferred_date": "weekday",
                "preferred_location_id": "123456",
                "preferred_location_name": "Cape Town",
                "id_number": "8808151569856",
                "asylum_seeker_number": None,
                "refugee_number": None,
                "passport_number": None,
                "passport_country": None,
                "data": {"result": "success"},
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        [reg] = VaccineRegistration.objects.all()
        self.assertEqual(reg.msisdn, "+27820001001")
        self.assertEqual(reg.source, "USSD")
        self.assertEqual(reg.gender, VaccineRegistration.GENDER_MALE)
        self.assertEqual(reg.first_name, "Test")
        self.assertEqual(reg.last_name, "Testing")
        self.assertEqual(reg.date_of_birth, now.date())
        self.assertEqual(reg.preferred_time, "morning")
        self.assertEqual(reg.preferred_date, "weekday")
        self.assertEqual(reg.preferred_location_id, "123456")
        self.assertEqual(reg.preferred_location_name, "Cape Town")
        self.assertEqual(reg.id_number, "8808151569856")
        self.assertEqual(reg.refugee_number, None)
        self.assertEqual(reg.asylum_seeker_number, None)
        self.assertEqual(reg.passport_number, None)
        self.assertEqual(reg.passport_country, None)
        self.assertEqual(reg.data, {"result": "success"})

    def test_duplicate_request(self):
        """
        Should create on the first request, and just return 200 on subsequent requests
        """
        now = timezone.now()
        user = get_user_model().objects.create_user("test")
        user.user_permissions.add(
            Permission.objects.get(codename="add_vaccineregistration")
        )
        self.client.force_authenticate(user)
        data = {
            "deduplication_id": "test-id",
            "msisdn": "27820001001",
            "source": "USSD",
            "gender": VaccineRegistration.GENDER_MALE,
            "first_name": "Test",
            "last_name": "Testing",
            "date_of_birth": now.strftime("%Y-%m-%d"),
            "preferred_time": "morning",
            "preferred_date": "weekday",
            "preferred_location_id": "123456",
            "preferred_location_name": "Cape Town",
            "id_number": "8808151569856",
            "asylum_seeker_number": None,
            "refugee_number": None,
            "passport_number": None,
            "passport_country": None,
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
