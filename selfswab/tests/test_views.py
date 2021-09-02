import json
import responses

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from unittest.mock import patch

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
                "age": SelfSwabScreen.Age.FROM_18_TO_40,
                "gender": SelfSwabScreen.Gender.FEMALE,
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
        self.assertEqual(selfswabscreen.age, SelfSwabScreen.Age.FROM_18_TO_40)
        self.assertEqual(selfswabscreen.gender, SelfSwabScreen.Gender.FEMALE)
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
                "result": SelfSwabTest.Result.NEGATIVE,
                "barcode": "CP159600001",
                "timestamp": "2020-01-11T08:30:24.922024+00:00",
                "updated_at": "2020-01-12T08:30:24.922024+00:00",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        [selfswabtest] = SelfSwabTest.objects.all()
        self.assertEqual(selfswabtest.msisdn, "27856454612")
        self.assertEqual(selfswabtest.result, SelfSwabTest.Result.NEGATIVE)
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
                "result": SelfSwabTest.Result.NEGATIVE,
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
                "result": SelfSwabTest.Result.NEGATIVE,
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
                "msisdn": "27836549876",
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
        self.assertEqual(registration.msisdn, "27836549876")

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
                "age": SelfSwabRegistration.Age.FROM_18_TO_40,
                "gender": SelfSwabRegistration.Gender.FEMALE,
                "opted_out": True,
                "optout_reason": SelfSwabRegistration.OptOutReason.TESTED_POSITIVE,
                "optout_timestamp": "2020-01-11T08:30:24.922024+00:00",
            },
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(response.json()["contact_id"], "CV0100H")

        [registration] = SelfSwabRegistration.objects.all()
        self.assertEqual(registration.age, SelfSwabRegistration.Age.FROM_18_TO_40)
        self.assertEqual(registration.gender, SelfSwabRegistration.Gender.FEMALE)
        self.assertTrue(registration.opted_out)
        self.assertEqual(
            registration.optout_reason,
            SelfSwabRegistration.OptOutReason.TESTED_POSITIVE,
        )
        self.assertEqual(
            registration.optout_timestamp.isoformat(),
            "2020-01-11T08:30:24.922024+00:00",
        )

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


class SelfSwabWhitelistViewSetTests(APITestCase):
    url = reverse("selfswab:rest_whitelist_contact")

    def test_unautorized(self):
        user = get_user_model().objects.create_user("test")

        response = self.client.post(
            self.url,
            {
                "msisdn": "27123123",
                "whitelist_group_uuid": "da85c55c-c213-4cfc-9d6d-c88d97993bf3",
            },
        )

        self.assertEqual(response.status_code, 401)

    def test_rapidpro_not_configured(self):
        user = get_user_model().objects.create_user("test")
        self.client.force_authenticate(user)

        response = self.client.post(
            self.url,
            {
                "msisdn": "27123123",
                "whitelist_group_uuid": "da85c55c-c213-4cfc-9d6d-c88d97993bf3",
            },
        )

        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json(), {"error": "rapidpro not configured"})

    @responses.activate
    @override_settings(
        RAPIDPRO_URL="https://rp-test.com", SELFSWAB_RAPIDPRO_TOKEN="123",
    )
    def test_contact_not_found(self):
        user = get_user_model().objects.create_user("test")
        self.client.force_authenticate(user)

        responses.add(
            responses.GET,
            f"https://rp-test.com/api/v2/contacts.json?urn=whatsapp:27123123",
            json={"next": None, "previous": None, "results": []},
        )

        responses.add(
            responses.POST,
            "https://rp-test.com/api/v2/contacts.json",
            json={
                "uuid": "09d23a05-47fe-11e4-bfe9-b8f6b119e9ab",
                "name": None,
                "language": "eng",
                "urns": ["whatsapp:27123123"],
                "groups": [
                    {
                        "name": "SelfSwab Whitelist",
                        "uuid": "da85c55c-c213-4cfc-9d6d-c88d97993bf3",
                    }
                ],
                "fields": {"msisdn": "27123123"},
                "blocked": False,
                "stopped": False,
                "created_on": "2015-11-11T13:05:57.457742Z",
                "modified_on": "2015-11-11T13:05:57.576056Z",
                "last_seen_on": None,
            },
        )

        response = self.client.post(
            self.url,
            {
                "msisdn": "27123123",
                "whitelist_group_uuid": "da85c55c-c213-4cfc-9d6d-c88d97993bf3",
            },
        )

        self.assertEqual(response.status_code, 201)

        [_, call] = responses.calls
        body = json.loads(call.request.body)
        self.assertEqual(
            body,
            {
                "language": "eng",
                "urns": ["whatsapp:27123123"],
                "fields": {"msisdn": "27123123"},
                "groups": ["da85c55c-c213-4cfc-9d6d-c88d97993bf3"],
            },
        )

    @responses.activate
    @override_settings(
        RAPIDPRO_URL="https://rp-test.com", SELFSWAB_RAPIDPRO_TOKEN="123",
    )
    def test_contact_exists_not_in_group(self):
        user = get_user_model().objects.create_user("test")
        self.client.force_authenticate(user)

        responses.add(
            responses.GET,
            f"https://rp-test.com/api/v2/contacts.json?urn=whatsapp:27123123",
            json={
                "next": None,
                "previous": None,
                "results": [
                    {
                        "uuid": "09d23a05-47fe-11e4-bfe9-b8f6b119e9ab",
                        "name": None,
                        "language": None,
                        "urns": ["whatsapp:27123123"],
                        "groups": [
                            {
                                "name": "Customers",
                                "uuid": "5a4eb79e-1b1f-4ae3-8700-09384cca385f",
                            }
                        ],
                        "fields": {},
                        "blocked": False,
                        "stopped": False,
                        "created_on": "2015-11-11T13:05:57.457742Z",
                        "modified_on": "2020-08-11T13:05:57.576056Z",
                        "last_seen_on": "2020-07-11T13:05:57.576056Z",
                    }
                ],
            },
        )

        responses.add(
            responses.GET,
            f"https://rp-test.com/api/v2/groups.json",
            json={
                "next": None,
                "previous": None,
                "results": [
                    {
                        "uuid": "8a8276de-6b58-4f82-83b7-c4ee21664c7c",
                        "name": "Some Dynamic Group",
                        "query": "Some Query",
                        "count": 111,
                    },
                    {
                        "uuid": "da85c55c-c213-4cfc-9d6d-c88d97993bf3",
                        "name": "SelfSwab Whitelist",
                        "query": None,
                        "count": 222,
                    },
                    {
                        "uuid": "5a4eb79e-1b1f-4ae3-8700-09384cca385f",
                        "name": "Customers",
                        "query": None,
                        "count": 333,
                    },
                ],
            },
        )

        responses.add(
            responses.POST,
            "https://rp-test.com/api/v2/contacts.json",
            json={
                "uuid": "09d23a05-47fe-11e4-bfe9-b8f6b119e9ab",
                "name": None,
                "language": "eng",
                "urns": ["whatsapp:27123123"],
                "groups": [
                    {
                        "name": "SelfSwab Whitelist",
                        "uuid": "da85c55c-c213-4cfc-9d6d-c88d97993bf3",
                    }
                ],
                "fields": {"msisdn": "27123123"},
                "blocked": False,
                "stopped": False,
                "created_on": "2015-11-11T13:05:57.457742Z",
                "modified_on": "2015-11-11T13:05:57.576056Z",
                "last_seen_on": None,
            },
        )

        response = self.client.post(
            self.url,
            {
                "msisdn": "27123123",
                "whitelist_group_uuid": "da85c55c-c213-4cfc-9d6d-c88d97993bf3",
            },
        )

        self.assertEqual(response.status_code, 200)

        [_, _, call] = responses.calls
        body = json.loads(call.request.body)
        self.assertEqual(
            body,
            {
                "groups": [
                    "5a4eb79e-1b1f-4ae3-8700-09384cca385f",
                    "da85c55c-c213-4cfc-9d6d-c88d97993bf3",
                ]
            },
        )

    @responses.activate
    @override_settings(
        RAPIDPRO_URL="https://rp-test.com", SELFSWAB_RAPIDPRO_TOKEN="123",
    )
    def test_contact_exists_in_group(self):
        user = get_user_model().objects.create_user("test")
        self.client.force_authenticate(user)

        responses.add(
            responses.GET,
            f"https://rp-test.com/api/v2/contacts.json?urn=whatsapp:27123123",
            json={
                "next": None,
                "previous": None,
                "results": [
                    {
                        "uuid": "09d23a05-47fe-11e4-bfe9-b8f6b119e9ab",
                        "name": None,
                        "language": None,
                        "urns": ["whatsapp:27123123"],
                        "groups": [
                            {
                                "name": "SelfSwab Whitelist",
                                "uuid": "da85c55c-c213-4cfc-9d6d-c88d97993bf3",
                            }
                        ],
                        "fields": {},
                        "blocked": False,
                        "stopped": False,
                        "created_on": "2015-11-11T13:05:57.457742Z",
                        "modified_on": "2020-08-11T13:05:57.576056Z",
                        "last_seen_on": "2020-07-11T13:05:57.576056Z",
                    }
                ],
            },
        )

        response = self.client.post(
            self.url,
            {
                "msisdn": "27123123",
                "whitelist_group_uuid": "da85c55c-c213-4cfc-9d6d-c88d97993bf3",
            },
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"error": "already whitelisted"})


class SendTestResultPDFViewViewSetTests(APITestCase):
    url = reverse("selfswab:rest_send_test_result_pdf")

    def test_unautorized(self):
        user = get_user_model().objects.create_user("test")

        response = self.client.post(self.url, {"barcode": "CP123",},)

        self.assertEqual(response.status_code, 401)

    def test_barcode_not_found(self):
        user = get_user_model().objects.create_user("test")
        self.client.force_authenticate(user)

        response = self.client.post(self.url, {"barcode": "CP123",},)

        self.assertEqual(response.status_code, 404)

    @patch("selfswab.views.send_whatsapp_media_message")
    def test_send_result_pdf(self, mock_send_whatsapp_media_message):
        user = get_user_model().objects.create_user("test")
        self.client.force_authenticate(user)

        SelfSwabTest.objects.create(
            **{
                "contact_id": "9e12d04c-af25-40b6-aa4f-57c72e8e3f91",
                "barcode": "CP159600001",
                "pdf_media_id": "media-uuid",
                "msisdn": "27123",
            }
        )

        response = self.client.post(self.url, {"barcode": "CP159600001",},)

        self.assertEqual(response.status_code, 200)

        mock_send_whatsapp_media_message.assert_called_with(
            "27123", "document", "media-uuid"
        )
