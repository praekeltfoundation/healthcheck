from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from selfswab.models import SelfSwabScreen, SelfSwabTest
from userprofile.tests.test_views import BaseEventTestCase


class SelfSwabScreenViewSetTests(APITestCase, BaseEventTestCase):
    url = reverse("selfswabscreen-list")

    def test_screen_data_validation(self):
        """
        The supplied data must be validated, and any errors returned
        """
        user = get_user_model().objects.create_user("test")
        user.user_permissions.add(Permission.objects.get(codename="add_selfswabscreen"))
        self.client.force_authenticate(user)
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_screen_successful_request(self):
        """
        Should create a new object in the database
        """
        user = get_user_model().objects.create_user("test")
        user.user_permissions.add(Permission.objects.get(codename="add_selfswabscreen"))
        self.client.force_authenticate(user)
        response = self.client.post(
            self.url,
            {
                "msisdn": "27856454612",
                "contact_id": "9e12d04c-af25-40b6-aa4f-57c72e8e3f91",
                "risk_type": SelfSwabScreen.HIGH_RISK,
                "registration": SelfSwabScreen.REGISTRATION_COMPLETE,
                "age": SelfSwabScreen.AGE_18T40,
                "gender": SelfSwabScreen.GENDER_FEMALE,
                "pre_existing_condition": "",
                "employee_number": "",
                "cough": True,
                "fever": True,
                "shortness_of_breath": False,
                "body_aches": True,
                "loss_of_taste_smell": False,
                "sore_throat": True,
                "additional_symptoms": False,
                "facility": "JHB Gen",
                "occupation": "nurse",
                "timestamp": "2020-01-11T08:30:24.922024+00:00",
            },
        )
        print(self.url)
        print(response.status_code)
        print(response.content)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        [selfswabscreen] = SelfSwabScreen.objects.all()
        # assert False
        self.assertEqual(
            selfswabscreen.registration, SelfSwabScreen.REGISTRATION_COMPLETE
        )
        self.assertEqual(selfswabscreen.msisdn, "27856454612")
        self.assertEqual(selfswabscreen.age, SelfSwabScreen.AGE_18T40)
        self.assertEqual(selfswabscreen.gender, SelfSwabScreen.GENDER_FEMALE)
        self.assertEqual(selfswabscreen.facility, "JHB Gen")
        self.assertEqual(
            selfswabscreen.contact_id, "9e12d04c-af25-40b6-aa4f-57c72e8e3f91"
        )
        self.assertEqual(selfswabscreen.risk_type, SelfSwabScreen.HIGH_RISK)
        self.assertEqual(selfswabscreen.pre_existing_condition, "")
        self.assertTrue(selfswabscreen.cough)
        self.assertTrue(selfswabscreen.fever)
        self.assertFalse(selfswabscreen.shortness_of_breath)
        self.assertTrue(selfswabscreen.body_aches)
        self.assertFalse(selfswabscreen.loss_of_taste_smell)
        self.assertTrue(selfswabscreen.sore_throat)
        self.assertFalse(selfswabscreen.additional_symptoms)
        self.assertEqual(selfswabscreen.occupation, "nurse")
        self.assertEqual(selfswabscreen.employee_number, "")


class SelfSwabTestViewSetTests(APITestCase, BaseEventTestCase):
    url = reverse("selfswabtest-list")

    def test_test_data_validation(self):
        """
        The supplied data must be validated, and any errors returned
        """
        user = get_user_model().objects.create_user("test")
        user.user_permissions.add(Permission.objects.get(codename="add_selfswabtest"))
        self.client.force_authenticate(user)
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_test_successful_request(self):
        """
        Should create a new object in the database
        """
        user = get_user_model().objects.create_user("test")
        user.user_permissions.add(Permission.objects.get(codename="add_selfswabtest"))
        self.client.force_authenticate(user)
        response = self.client.post(
            self.url,
            {
                "msisdn": "27856454612",
                "contact_id": "9e12d04c-af25-40b6-aa4f-57c72e8e3f91",
                "result": SelfSwabTest.RESULT_NEGATIVE,
                "barcode": "1234567",
                "timestamp": "2020-01-11T08:30:24.922024+00:00",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        [selfswabtest] = SelfSwabTest.objects.all()
        self.assertEqual(selfswabtest.msisdn, "27856454612")
        self.assertEqual(selfswabtest.result, SelfSwabTest.RESULT_NEGATIVE)
        self.assertEqual(
            selfswabtest.contact_id, "9e12d04c-af25-40b6-aa4f-57c72e8e3f91"
        )
        self.assertEqual(selfswabtest.barcode, "1234567")
