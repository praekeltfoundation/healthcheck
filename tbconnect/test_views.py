from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from userprofile.tests.test_views import BaseEventTestCase

from .models import TBCheck


class TBCheckViewSetTests(APITestCase, BaseEventTestCase):
    url = reverse("tbcheck-list")

    def test_data_validation(self):
        """
        The supplied data must be validated, and any errors returned
        """
        user = get_user_model().objects.create_user("test")
        user.user_permissions.add(Permission.objects.get(codename="add_tbcheck"))
        self.client.force_authenticate(user)
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_successful_request(self):
        """
        Should create a new TBCheck object in the database
        """
        user = get_user_model().objects.create_user("test")
        user.user_permissions.add(Permission.objects.get(codename="add_tbcheck"))
        self.client.force_authenticate(user)
        response = self.client.post(
            self.url,
            {
                "msisdn": "27856454612",
                "source": "USSD",
                "province": "ZA-WC",
                "city": "Cape Town",
                "age": "18-40",
                "gender": "female",
                "cough": "yes_gt_2weeks",
                "fever": True,
                "sweat": False,
                "weight": True,
                "exposure": "yes",
                "tracing": True,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        [tbcheck] = TBCheck.objects.all()
        self.assertEqual(tbcheck.msisdn, "27856454612")
        self.assertEqual(tbcheck.source, "USSD")
        self.assertEqual(tbcheck.province, "ZA-WC")
        self.assertEqual(tbcheck.city, "Cape Town")
        self.assertEqual(tbcheck.age, "18-40")
        self.assertEqual(tbcheck.gender, "female")
        self.assertEqual(tbcheck.cough, "yes_gt_2weeks")
        self.assertTrue(tbcheck.fever)
        self.assertFalse(tbcheck.sweat)
        self.assertTrue(tbcheck.weight)
        self.assertEqual(tbcheck.exposure, "yes")
        self.assertTrue(tbcheck.tracing)
