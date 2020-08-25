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
                "age": TBCheck.AGE_18T40,
                "gender": TBCheck.GENDER_FEMALE,
                "cough": TBCheck.COUGH_YES_GT_2WEEKS,
                "fever": True,
                "sweat": False,
                "weight": True,
                "exposure": "yes",
                "tracing": True,
                "risk": TBCheck.RISK_LOW,
                "location": "+40.20361+40.20361",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        [tbcheck] = TBCheck.objects.all()
        self.assertEqual(tbcheck.msisdn, "27856454612")
        self.assertEqual(tbcheck.source, "USSD")
        self.assertEqual(tbcheck.province, "ZA-WC")
        self.assertEqual(tbcheck.city, "Cape Town")
        self.assertEqual(tbcheck.age, TBCheck.AGE_18T40)
        self.assertEqual(tbcheck.gender, TBCheck.GENDER_FEMALE)
        self.assertEqual(tbcheck.cough, TBCheck.COUGH_YES_GT_2WEEKS)
        self.assertTrue(tbcheck.fever)
        self.assertFalse(tbcheck.sweat)
        self.assertTrue(tbcheck.weight)
        self.assertEqual(tbcheck.exposure, "yes")
        self.assertTrue(tbcheck.tracing)
        self.assertEqual(tbcheck.risk, TBCheck.RISK_LOW)
        self.assertEqual(tbcheck.location, "+40.20361+40.20361")
