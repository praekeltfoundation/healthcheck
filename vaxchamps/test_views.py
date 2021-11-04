import json

import responses
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from vaxchamps.views import rapidpro_client


class RegistrationViewSetTests(APITestCase):
    def setUp(self):
        responses.add(
            responses.POST,
            "https://whatsapp.turn.io/v1/contacts",
            json={"contacts": [{"status": "valid"}]},
        )
        rapidpro_client.root_url = "https://textit.in/api/v2"
        responses.add(
            responses.POST,
            "https://textit.in/api/v2/flow_starts.json",
            json={
                "uuid": "09d23a05-47fe-11e4-bfe9-b8f6b119e9ab",
                "flow": {
                    "uuid": "f5901b62-ba76-4003-9c62-72fdacc1b7b7",
                    "name": "Thrift Shop",
                },
                "groups": [],
                "contacts": [],
                "restart_participants": True,
                "extra": {},
                "status": "complete",
                "created_on": "2013-08-19T19:11:21.082Z",
                "modified_on": "2013-08-19T19:11:21.082Z",
            },
        )
        user = get_user_model().objects.create_user("test")
        user.user_permissions.add(
            Permission.objects.get(codename="create_registration")
        )
        self.client.force_authenticate(user)

    @responses.activate
    def test_valid_registration(self):
        url = reverse("registrations-list")
        data = {
            "name": "test name",
            "cell_no": "0820001001",
            "lang": 1,
            "comms_choice": 1,
            "email": "test@example.org",
            "popia_consent": 0,
            "province": 9,
            "district": 49,
            "gender": 2,
            "age": 3,
        }
        with self.settings(
            VAXCHAMPS_RAPIDPRO_FLOW="fde8a8e4-b973-42e4-aa96-dbc5ef70164d"
        ):
            response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        [_, request] = responses.calls
        self.assertEqual(
            json.loads(request.request.body)["extra"],
            {
                "age": "18-34",
                "cell_no": "+27820001001",
                "comms_choice": 1,
                "district": "City of Cape Town",
                "email": "test@example.org",
                "gender": "Male",
                "lang": "eng",
                "name": "test name",
                "popia_consent": 0,
                "province": "Western Cape",
            },
        )
