import json
import uuid

import responses
from django.test import TestCase, override_settings
from django.utils import timezone
from selfswab.models import SelfSwabTest
from selfswab.tasks import poll_meditech_api_for_results


class PollMeditechForResults(TestCase):
    updated_at = timezone.now()
    test_timestamp = "2020-12-16T10:14:05+00:00"

    flow_response = {
        "uuid": "93a624ad-5440-415e-b49f-17bf42754acb",
        "flow": {
            "uuid": "f5901b62-ba76-4003-9c62-72fdacc1b7b7",
            "name": "SelfSwabTest",
        },
        "groups": [
            {"uuid": "04a4752b-0f49-480e-ae60-3a3f2bea485c", "name": "SelfSwabStudy"}
        ],
        "contacts": [{"uuid": "5079cb96-a1d8-4f47-8c87-d8c7bb6ddab9", "name": "Joe"}],
        "restart_participants": True,
        "status": "pending",
        "created_on": "2015-08-26T10:04:09.737686+00:00",
        "modified_on": "2015-09-26T10:04:09.737686+00:00",
        "extra": {"result": "Negative", "updated_at": updated_at.strftime("%d/%m/%Y")},
    }

    def create_selfswab_test(self, msisdn, barcode, result=SelfSwabTest.RESULT_PENDING):
        return SelfSwabTest.objects.create(
            **{
                "id": uuid.uuid4().hex,
                "contact_id": "9e12d04c-af25-40b6-aa4f-57c72e8e3f91",
                "msisdn": msisdn,
                "result": result,
                "barcode": barcode,
                "timestamp": self.updated_at,
            }
        )

    @responses.activate
    @override_settings(
        RAPIDPRO_URL="https://rp-test.com",
        MEDITECH_URL="https://medi-test.com",
        MEDITECH_USER="praekelt",
        MEDITECH_PASSWORD="secret",
        SELFSWAB_RAPIDPRO_TOKEN="123",
        SELFSWAB_RAPIDPRO_FLOW="321",
    )
    def test_poll_to_meditech_for_results(self):
        """
        Should sync a barcode and get results from api,
        and save result
        """
        test1 = self.create_selfswab_test("27856454612", "12345678")
        test2 = self.create_selfswab_test("27895671234", "87654321")
        test3 = self.create_selfswab_test(
            "27890001234", "12341234", SelfSwabTest.RESULT_POSITIVE
        )

        responses.add(
            responses.POST,
            "https://medi-test.com",
            json={
                "results": [
                    {"barcode": "12345678", "result": ""},
                    {
                        "barcode": "87654321",
                        "result": "NEGATIVE",
                        "collDateTime": self.test_timestamp,
                        "recvDateTime": self.test_timestamp,
                        "verifyDateTime": self.test_timestamp,
                    },
                ]
            },
        )

        responses.add(
            responses.POST,
            "https://rp-test.com/api/v2/flow_starts.json",
            json=self.flow_response,
        )

        poll_meditech_api_for_results()

        [call1, call2] = responses.calls

        body2 = json.loads(call2.request.body)
        body1 = json.loads(call1.request.body)

        self.assertEqual(body1, {"barcodes": ["12345678", "87654321"]})
        self.assertEqual(
            body2,
            {
                "flow": "321",
                "urns": ["whatsapp:27895671234"],
                "extra": {
                    "result": "Negative",
                    "updated_at": self.updated_at.strftime("%d/%m/%Y"),
                },
            },
        )

        test1.refresh_from_db()
        test2.refresh_from_db()
        test3.refresh_from_db()

        self.assertEqual(test1.result, SelfSwabTest.RESULT_PENDING)
        self.assertIsNone(test1.collection_timestamp)
        self.assertIsNone(test1.received_timestamp)
        self.assertIsNone(test1.authorized_timestamp)

        self.assertEqual(test2.result, SelfSwabTest.RESULT_NEGATIVE)
        self.assertEqual(test2.collection_timestamp.isoformat(), self.test_timestamp)
        self.assertEqual(test2.received_timestamp.isoformat(), self.test_timestamp)
        self.assertEqual(test2.authorized_timestamp.isoformat(), self.test_timestamp)

        self.assertEqual(test3.result, SelfSwabTest.RESULT_POSITIVE)
        self.assertIsNone(test3.collection_timestamp)
        self.assertIsNone(test3.received_timestamp)
        self.assertIsNone(test3.authorized_timestamp)

    @responses.activate
    @override_settings(
        RAPIDPRO_URL="https://rp-test.com",
        MEDITECH_URL="https://medi-test.com",
        MEDITECH_USER="praekelt",
        MEDITECH_PASSWORD="secret",
        SELFSWAB_RAPIDPRO_TOKEN="123",
        SELFSWAB_RAPIDPRO_FLOW="321",
    )
    def test_poll_to_meditech_barcode_does_not_exist(self):
        """
        Should try get results from api with barcodes that
        dont exist, assert that no api calls are made
        """
        self.create_selfswab_test("27856454612", "12345678")
        self.create_selfswab_test("27895671234", "87654321")

        responses.add(
            responses.POST,
            "https://medi-test.com",
            json={
                "results": [
                    {"barcode": "12121212", "result": ""},
                    {
                        "barcode": "88888888",
                        "result": "NEGATIVE",
                        "collDateTime": self.test_timestamp,
                        "recvDateTime": self.test_timestamp,
                        "verifyDateTime": self.test_timestamp,
                    },
                ]
            },
        )

        responses.add(
            responses.POST,
            "https://rp-test.com/api/v2/flow_starts.json",
            json=self.flow_response,
        )

        poll_meditech_api_for_results()

        self.assertEqual(len(responses.calls), 1)

    @responses.activate
    @override_settings(
        RAPIDPRO_URL="https://rp-test.com",
        MEDITECH_URL="https://medi-test.com",
        MEDITECH_USER="praekelt",
        MEDITECH_PASSWORD="secret",
        SELFSWAB_RAPIDPRO_TOKEN="123",
        SELFSWAB_RAPIDPRO_FLOW="321",
    )
    def test_poll_to_meditech_duplicate_barcode(self):
        """
        Should not fail if there is a duplicate barcode
        """
        self.create_selfswab_test("27856454612", "12345678")
        self.create_selfswab_test("27895671234", "12345678")

        responses.add(
            responses.POST,
            "https://medi-test.com",
            json={"results": [{"barcode": "12345678", "result": ""}]},
        )

        poll_meditech_api_for_results()

        self.assertEqual(len(responses.calls), 1)
