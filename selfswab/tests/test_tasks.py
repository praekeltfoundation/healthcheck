import json

import responses
from django.test import TestCase, override_settings
from django.utils import timezone
from selfswab.models import SelfSwabTest
from selfswab.tasks import poll_meditech_api_for_results


class PollMeditechForResults(TestCase):
    updated_at = timezone.now()

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

    @responses.activate
    @override_settings(
        RAPIDPRO_URL="https://rp-test.com",
        MEDITECH_URL="https://medi-test.com",
        MEDITECH_USER="praekelt",
        MEDITECH_PASSWORD="secret",
        SELFSWAB_RAPIDPRO_TOKEN="123",
        SELFSWAB_RAPIDPRO_FLOW="321",
    )
    def test_poll_to_meditch_for_results(self):
        """
        Should sync a barcode and get results from api,
        and save result
        """
        SelfSwabTest.objects.create(
            **{
                "id": "3d9dc41c-8c18-4e3f-8afc-8970b1cae7c1",
                "contact_id": "9e12d04c-af25-40b6-aa4f-57c72e8e3f91",
                "msisdn": "27856454612",
                "result": "Pending",
                "barcode": "12345678",
                "timestamp": self.updated_at,
            }
        )
        SelfSwabTest.objects.create(
            **{
                "id": "9a4c5a43-9a48-44b0-ad32-8561217461c1",
                "contact_id": "9e12d7hj-af25-40b6-bb4f-57c72c3c3f91",
                "msisdn": "27895671234",
                "result": "Pending",
                "barcode": "87654321",
                "timestamp": self.updated_at,
            }
        )
        SelfSwabTest.objects.create(
            **{
                "id": "2da90072-f23c-4690-b1d0-e89aaddb982c",
                "contact_id": "9e12d04c-af25-40b6-aa4f-57c72e8e3f91",
                "msisdn": "27890001234",
                "result": "Positive",
                "barcode": "12341234",
                "timestamp": self.updated_at,
            }
        )

        responses.add(
            responses.POST,
            "https://medi-test.com",
            json={"barcodes": {"12345678": "", "87654321": "Negative"}},
        )

        responses.add(
            responses.POST,
            "https://rp-test.com/api/v2/flow_starts.json",
            json=self.flow_response,
        )

        poll_meditech_api_for_results()

        [call1, call2, call3] = responses.calls

        body3 = json.loads(call3.request.body)
        body2 = json.loads(call2.request.body)
        body1 = json.loads(call1.request.body)

        self.assertEqual(body1, {"barcodes": ["12345678", "87654321"]})
        self.assertEqual(
            body2,
            {
                "flow": "321",
                "urns": ["whatsapp:27856454612"],
                "extra": {
                    "result": "Pending",
                    "updated_at": self.updated_at.strftime("%d/%m/%Y"),
                },
            },
        )
        self.assertEqual(
            body3,
            {
                "flow": "321",
                "urns": ["whatsapp:27895671234"],
                "extra": {
                    "result": "Negative",
                    "updated_at": self.updated_at.strftime("%d/%m/%Y"),
                },
            },
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
    def test_poll_to_meditch_for_result_mapping(self):
        """
        Should sync a barcode and get results from api,
        and save result
        """
        SelfSwabTest.objects.create(
            **{
                "id": "3d9dc41c-8c18-4e3f-8afc-8970b1cae7c1",
                "contact_id": "9e12d04c-af25-40b6-aa4f-57c72e8e3f91",
                "msisdn": "27856454612",
                "result": "Pending",
                "barcode": "12345678",
                "timestamp": self.updated_at,
            }
        )
        SelfSwabTest.objects.create(
            **{
                "id": "9a4c5a43-9a48-44b0-ad32-8561217461c1",
                "contact_id": "9e12d7hj-af25-40b6-bb4f-57c72c3c3f91",
                "msisdn": "27895671234",
                "result": "Pending",
                "barcode": "87654321",
                "timestamp": self.updated_at,
            }
        )
        SelfSwabTest.objects.create(
            **{
                "id": "2da90072-f23c-4690-b1d0-e89aaddb982c",
                "contact_id": "9e12d04c-af25-40b6-aa4f-57c72e8e3f91",
                "msisdn": "27890001234",
                "result": "Pending",
                "barcode": "12341234",
                "timestamp": self.updated_at,
            }
        )
        SelfSwabTest.objects.create(
            **{
                "id": "c1864ae9-767a-491b-96f9-e8ab4b435b9a",
                "contact_id": "9e12d04c-af25-40b6-aa4f-57c72e8e3f91",
                "msisdn": "27890001212",
                "result": "Pending",
                "barcode": "12121212",
                "timestamp": self.updated_at,
            }
        )

        responses.add(
            responses.POST,
            "https://medi-test.com",
            json={
                "barcodes": {
                    "12345678": "POS",
                    "87654321": "NOT DET",
                    "12341234": "REJ",
                    "12121212": "INCON",
                }
            },
        )

        responses.add(
            responses.POST,
            "https://rp-test.com/api/v2/flow_starts.json",
            json=self.flow_response,
        )

        poll_meditech_api_for_results()

        [call1, call2, call3, call4, call5] = responses.calls

        body5 = json.loads(call5.request.body)
        body4 = json.loads(call4.request.body)
        body3 = json.loads(call3.request.body)
        body2 = json.loads(call2.request.body)
        body1 = json.loads(call1.request.body)

        self.assertEqual(
            body1, {"barcodes": ["12345678", "87654321", "12341234", "12121212"]}
        )
        self.assertEqual(
            body2,
            {
                "flow": "321",
                "urns": ["whatsapp:27856454612"],
                "extra": {
                    "result": "Positive",
                    "updated_at": self.updated_at.strftime("%d/%m/%Y"),
                },
            },
        )
        self.assertEqual(
            body3,
            {
                "flow": "321",
                "urns": ["whatsapp:27895671234"],
                "extra": {
                    "result": "Negative",
                    "updated_at": self.updated_at.strftime("%d/%m/%Y"),
                },
            },
        )
        self.assertEqual(
            body4,
            {
                "flow": "321",
                "urns": ["whatsapp:27890001234"],
                "extra": {
                    "result": "Rejected",
                    "updated_at": self.updated_at.strftime("%d/%m/%Y"),
                },
            },
        )
        self.assertEqual(
            body5,
            {
                "flow": "321",
                "urns": ["whatsapp:27890001212"],
                "extra": {
                    "result": "Invalid",
                    "updated_at": self.updated_at.strftime("%d/%m/%Y"),
                },
            },
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
    def test_poll_to_meditch_barcode_does_not_exist(self):
        """
        Should try get results from api with barcodes that
        dont exist, assert that no api calls are made
        """
        SelfSwabTest.objects.create(
            **{
                "id": "3d9dc41c-8c18-4e3f-8afc-8970b1cae7c1",
                "contact_id": "9e12d04c-af25-40b6-aa4f-57c72e8e3f91",
                "msisdn": "27856454612",
                "result": "",
                "barcode": "12345678",
                "timestamp": self.updated_at,
            }
        )
        SelfSwabTest.objects.create(
            **{
                "id": "9a4c5a43-9a48-44b0-ad32-8561217461c1",
                "contact_id": "9e12d7hj-af25-40b6-bb4f-57c72c3c3f91",
                "msisdn": "27895671234",
                "result": "",
                "barcode": "87654321",
                "timestamp": self.updated_at,
            }
        )

        responses.add(
            responses.POST,
            "https://medi-test.com",
            json={"barcodes": {"12121212": "", "88888888": "Negative"}},
        )

        responses.add(
            responses.POST,
            "https://rp-test.com/api/v2/flow_starts.json",
            json=self.flow_response,
        )

        poll_meditech_api_for_results()

        self.assertEqual(len(responses.calls), 1)
