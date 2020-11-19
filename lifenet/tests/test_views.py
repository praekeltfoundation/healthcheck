from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from lifenet.models import LNCheck
from userprofile.models import HealthCheckUserProfile
from userprofile.tests.test_views import BaseEventTestCase


class LNCheckViewSetTests(APITestCase, BaseEventTestCase):
    url = reverse("lncheck-list")

    def test_data_validation(self):
        """
        The supplied data must be validated, and any errors returned
        """
        user = get_user_model().objects.create_user("test")
        user.user_permissions.add(Permission.objects.get(codename="add_lncheck"))
        self.client.force_authenticate(user)
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_successful_request(self):
        """
        Should create a new LNCheck object in the database
        """
        user = get_user_model().objects.create_user("test")
        user.user_permissions.add(Permission.objects.get(codename="add_lncheck"))
        self.client.force_authenticate(user)
        response = self.client.post(
            self.url,
            {
                "msisdn": "27856454612",
                "source": "WhatsApp",
                "age": LNCheck.Age.AGE_18T39,
                "cough": True,
                "fever": True,
                "sore_throat": False,
                "difficulty_breathing": True,
                "tracing": True,
                "muscle_pain": True,
                "smell": True,
                "exposure": "yes",
                "risk": LNCheck.Risk.RISK_LOW,
                "language": "eng",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        [lncheck] = LNCheck.objects.all()
        self.assertEqual(lncheck.msisdn, "27856454612")
        self.assertEqual(lncheck.source, "WhatsApp")
        self.assertEqual(lncheck.age, LNCheck.AGE_18T39)
        self.assertTrue(lncheck.cough)
        self.assertTrue(lncheck.fever)
        self.assertFalse(lncheck.sore_throat)
        self.assertTrue(lncheck.difficulty_breathing)
        self.assertEqual(lncheck.exposure, "yes")
        self.assertTrue(lncheck.tracing)
        self.assertEqual(lncheck.risk, LNCheck.RISK_LOW)
        self.assertEqual(lncheck.language, "eng")

    def test_creates_user_profile(self):
        """
        The user profile should be created when the LN Check is saved
        """
        user = get_user_model().objects.create_user("test")
        user.user_permissions.add(Permission.objects.get(codename="add_lncheck"))
        self.client.force_authenticate(user)
        response = self.client.post(
            self.url,
            {
                "msisdn": "27856454612",
                "source": "WhatsApp",
                "age": LNCheck.Age.AGE_18T39,
                "cough": False,
                "fever": False,
                "sore_throat": False,
                "difficulty_breathing": False,
                "tracing": True,
                "muscle_pain": True,
                "smell": True,
                "exposure": "yes",
                "risk": LNCheck.Risk.RISK_LOW,
                "language": "eng",
            },
            format="json",
        )
        profile = HealthCheckUserProfile.objects.get(msisdn="27856454612")
        self.assertEqual(profile.age, LNCheck.AGE_18T39)
