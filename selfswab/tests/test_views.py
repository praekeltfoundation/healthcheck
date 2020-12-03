from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from selfswab.models import SelfSwabRegistration, SelfSwabScreen, SelfSwabTest
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
                "age": SelfSwabScreen.AGE_18T40,
                "gender": SelfSwabScreen.GENDER_FEMALE,
                "pre_existing_condition": "",
                "employee_number": "20123123117/04",
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

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        [selfswabscreen] = SelfSwabScreen.objects.all()
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
        self.assertEqual(selfswabscreen.employee_number, "20123123117/04")
        self.assertTrue(selfswabscreen.should_sync)


class SelfSwabTestViewSetTests(APITestCase, BaseEventTestCase):
    url = reverse("selfswabtest-list")

    def test_data_validation(self):
        """
        The supplied data must be validated, and any errors returned
        """
        user = get_user_model().objects.create_user("test")
        user.user_permissions.add(Permission.objects.get(codename="add_selfswabtest"))
        self.client.force_authenticate(user)
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_successful_request(self):
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
                "barcode": "CP159600001",
                "timestamp": "2020-01-11T08:30:24.922024+00:00",
                "updated_at": "2020-01-12T08:30:24.922024+00:00",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        [selfswabtest] = SelfSwabTest.objects.all()
        self.assertEqual(selfswabtest.msisdn, "27856454612")
        self.assertEqual(selfswabtest.result, SelfSwabTest.RESULT_NEGATIVE)
        self.assertEqual(
            selfswabtest.contact_id, "9e12d04c-af25-40b6-aa4f-57c72e8e3f91"
        )
        self.assertEqual(selfswabtest.barcode, "CP159600001")

    def test_duplicate_barcode_request(self):
        """
        Should return an error when the barcode already exists in the database
        """
        user = get_user_model().objects.create_user("test")
        user.user_permissions.add(Permission.objects.get(codename="add_selfswabtest"))
        self.client.force_authenticate(user)

        SelfSwabTest.objects.create(
            **{
                "contact_id": "9e12d04c-af25-40b6-aa4f-57c72e8e3f91",
                "barcode": "CP159600001",
            }
        )

        response = self.client.post(
            self.url,
            {
                "msisdn": "27856454612",
                "contact_id": "9e12d04c-af25-40b6-aa4f-57c72e8e3f91",
                "result": SelfSwabTest.RESULT_NEGATIVE,
                "barcode": "CP159600001",
                "timestamp": "2020-01-11T08:30:24.922024+00:00",
                "updated_at": "2020-01-12T08:30:24.922024+00:00",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.json(),
            {"barcode": ["self swab test with this barcode already exists."]},
        )
        self.assertEqual(SelfSwabTest.objects.all().count(), 1)

    def test_invalid_barcode_request(self):
        """
        Should return an error when the barcode is not a valid format
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
                "barcode": "invalid",
                "timestamp": "2020-01-11T08:30:24.922024+00:00",
                "updated_at": "2020-01-12T08:30:24.922024+00:00",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), {"detail": "barcode invalid format."})
        self.assertEqual(SelfSwabTest.objects.all().count(), 0)


class SelfSwabRegistrationViewSetTests(APITestCase, BaseEventTestCase):
    url = reverse("selfswabregistration-list")

    def create_registration(self, contact_id):
        return SelfSwabRegistration.objects.create(
            **{"contact_id": contact_id, "employee_number": "test"}
        )

    def test_data_validation(self):
        """
        The supplied data must be validated, and any errors returned
        """
        user = get_user_model().objects.create_user("test")
        user.user_permissions.add(
            Permission.objects.get(codename="add_selfswabregistration")
        )
        self.client.force_authenticate(user)
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_successful_request(self):
        """
        Should create a new object in the database
        """
        user = get_user_model().objects.create_user("test")
        user.user_permissions.add(
            Permission.objects.get(codename="add_selfswabregistration")
        )
        self.client.force_authenticate(user)

        self.create_registration("CV0100H")
        self.create_registration("CV0102H")

        response = self.client.post(
            self.url,
            {
                "employee_number": "emp-123",
                "first_name": "first",
                "last_name": "last",
                "facility": "JHB Gen",
                "occupation": "doctor",
            },
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(response.json()["contact_id"], "CV0101H")

        [registration] = SelfSwabRegistration.objects.all().exclude(
            employee_number="test"
        )
        self.assertEqual(registration.employee_number, "emp-123")
        self.assertEqual(registration.contact_id, "CV0101H")
        self.assertEqual(registration.first_name, "first")
        self.assertEqual(registration.last_name, "last")
        self.assertEqual(registration.facility, "JHB Gen")
        self.assertEqual(registration.occupation, "doctor")

    def test_successful_patch_request(self):
        """
        Should create a new object in the database
        """
        user = get_user_model().objects.create_user("test")
        user.user_permissions.add(
            Permission.objects.get(codename="change_selfswabregistration")
        )
        self.client.force_authenticate(user)

        registration = self.create_registration("CV0100H")

        url = reverse("selfswabregistration-detail", args=(registration.id,))

        response = self.client.patch(
            url,
            {
                "age": SelfSwabRegistration.AGE_18T40,
                "gender": SelfSwabRegistration.GENDER_OTHER,
            },
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(response.json()["contact_id"], "CV0100H")

        [registration] = SelfSwabRegistration.objects.all()
        self.assertEqual(registration.age, SelfSwabRegistration.AGE_18T40)
        self.assertEqual(registration.gender, SelfSwabRegistration.GENDER_OTHER)

    def test_request_with_contact_id(self):
        """
        Should create a new object in the database
        """
        user = get_user_model().objects.create_user("test")
        user.user_permissions.add(
            Permission.objects.get(codename="add_selfswabregistration")
        )
        self.client.force_authenticate(user)
        response = self.client.post(
            self.url,
            {
                "employee_number": "emp-123",
                "first_name": "first",
                "last_name": "last",
                "facility": "JHB Gen",
                "occupation": "doctor",
                "contact_id": "CV1111H",
            },
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(response.json()["contact_id"], "CV1111H")

        [registration] = SelfSwabRegistration.objects.all()
        self.assertEqual(registration.contact_id, "CV1111H")
