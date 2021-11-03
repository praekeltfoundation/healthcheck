import json

import responses
from django.test import TestCase

from vaxchamps.serializers import RegistrationSerializer


class RegistrationSerializerTests(TestCase):
    def setUp(self):
        responses.add(
            responses.POST,
            "https://whatsapp.turn.io/v1/contacts",
            json={"contacts": [{"status": "valid"}]},
        )

    def test_required_field(self):
        serializer = RegistrationSerializer(data={})
        self.assertFalse(serializer.is_valid())
        self.assertEqual(
            serializer.errors,
            {
                "name": ["This field is required."],
                "cell_no": ["This field is required."],
                "lang": ["This field is required."],
                "comms_choice": ["This field is required."],
                "popia_consent": ["This field is required."],
            },
        )

    @responses.activate
    def test_success(self):
        serializer = RegistrationSerializer(
            data={
                "name": "test name",
                "cell_no": "0820001001",
                "lang": 1,
                "comms_choice": 1,
                "popia_consent": 0,
            }
        )
        self.assertTrue(serializer.is_valid())
        [request] = responses.calls
        self.assertEqual(
            json.loads(request.request.body),
            {"blocking": "wait", "contacts": ["+27820001001"]},
        )

    @responses.activate
    def test_not_whatsapp_contact(self):
        responses.reset()
        responses.add(
            responses.POST,
            "https://whatsapp.turn.io/v1/contacts",
            json={"contacts": [{"status": "invalid"}]},
        )
        serializer = RegistrationSerializer(
            data={
                "name": "test name",
                "cell_no": "0820001001",
                "lang": 1,
                "comms_choice": 1,
                "popia_consent": 0,
            }
        )
        self.assertFalse(serializer.is_valid())
        self.assertEqual(serializer.errors, {"cell_no": ["not a WhatsApp contact"]})

    @responses.activate
    def test_province_missing_validation(self):
        serializer = RegistrationSerializer(
            data={
                "name": "test name",
                "cell_no": "0820001001",
                "lang": 1,
                "comms_choice": 1,
                "popia_consent": 0,
                "district": 1,
            }
        )
        self.assertFalse(serializer.is_valid())
        self.assertEqual(
            serializer.errors,
            {"non_field_errors": ["province is required if district is provided"]},
        )

    @responses.activate
    def test_district_in_province_validation(self):
        serializer = RegistrationSerializer(
            data={
                "name": "test name",
                "cell_no": "0820001001",
                "lang": 1,
                "comms_choice": 1,
                "popia_consent": 0,
                "province": 1,
                "district": 11,
            }
        )
        self.assertFalse(serializer.is_valid())
        self.assertEqual(
            serializer.errors,
            {
                "non_field_errors": [
                    "district must be one of [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]"
                ]
            },
        )
