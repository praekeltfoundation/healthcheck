import json

import responses
from django.test import TestCase, override_settings
from django.utils import timezone

from tbconnect.models import TBCheck
from tbconnect.tasks import perform_sync_to_rapidpro
from userprofile.models import HealthCheckUserProfile


class SyncToRapidproTests(TestCase):
    flow_response = {
        "uuid": "93a624ad-5440-415e-b49f-17bf42754acb",
        "flow": {
            "uuid": "f5901b62-ba76-4003-9c62-72fdacc1b7b7",
            "name": "Registration",
        },
        "groups": [
            {"uuid": "04a4752b-0f49-480e-ae60-3a3f2bea485c", "name": "The A-Team"}
        ],
        "contacts": [
            {"uuid": "5079cb96-a1d8-4f47-8c87-d8c7bb6ddab9", "name": "Joe"},
            {"uuid": "28291a83-157e-45ed-93ef-e0425a065d35", "name": "Frank"},
        ],
        "restart_participants": True,
        "status": "pending",
        "extra": {"day": "Monday"},
        "created_on": "2015-08-26T10:04:09.737686+00:00",
        "modified_on": "2015-09-26T10:04:09.737686+00:00",
    }
    completed_timestamp = timezone.now()

    def create_profile_and_check(
        self,
        msisdn="+27830000001",
        optin=True,
        synced=False,
        source="WhatsApp",
        risk=TBCheck.RISK_HIGH,
    ):
        TBCheck.objects.create(
            **{
                "msisdn": msisdn,
                "fever": True,
                "sweat": True,
                "weight": True,
                "tracing": True,
                "source": source,
                "completed_timestamp": self.completed_timestamp,
                "risk": risk,
            }
        )

        return HealthCheckUserProfile.objects.create(
            **{
                "msisdn": msisdn,
                "data": {"follow_up_optin": optin, "synced_to_tb_rapidpro": synced},
            }
        )

    @responses.activate
    @override_settings(
        RAPIDPRO_URL="https://rp-test.com",
        RAPIDPRO_TOKEN="123",
        RAPIDPRO_TBCONNECT_FLOW="321",
    )
    def test_sync_whatsapp(self):
        """
        Should sync a profile created from WhatsApp, only if opted in and not
        synced before
        """
        profile = self.create_profile_and_check()
        self.create_profile_and_check("+27830000002", False)
        self.create_profile_and_check("+27830000003", True, True)

        responses.add(
            responses.POST,
            f"https://rp-test.com/api/v2/flow_starts.json",
            json=self.flow_response,
        )

        perform_sync_to_rapidpro()

        profile.refresh_from_db()
        self.assertTrue(profile.data["synced_to_tb_rapidpro"])

        [call] = responses.calls
        body = json.loads(call.request.body)
        self.assertEqual(
            body,
            {
                "flow": "321",
                "urns": ["whatsapp:27830000001"],
                "extra": {
                    "risk": "high",
                    "source": "WhatsApp",
                    "completed_timestamp": self.completed_timestamp.strftime(
                        "%d/%m/%Y"
                    ),
                },
            },
        )

    @responses.activate
    @override_settings(
        RAPIDPRO_URL="https://rp-test.com",
        RAPIDPRO_TOKEN="123",
        RAPIDPRO_TBCONNECT_FLOW="321",
    )
    def test_sync_sms(self):
        """
        Should sync a profile created from USSD as SMS
        """
        profile = self.create_profile_and_check(source="USSD")

        responses.add(
            responses.POST,
            f"https://rp-test.com/api/v2/flow_starts.json",
            json=self.flow_response,
        )

        perform_sync_to_rapidpro()

        profile.refresh_from_db()

        self.assertTrue(profile.data["synced_to_tb_rapidpro"])

        [call] = responses.calls
        body = json.loads(call.request.body)
        self.assertEqual(
            body,
            {
                "flow": "321",
                "urns": ["tel:+27830000001"],
                "extra": {
                    "risk": "high",
                    "source": "USSD",
                    "completed_timestamp": self.completed_timestamp.strftime(
                        "%d/%m/%Y"
                    ),
                },
            },
        )

    @responses.activate
    @override_settings(
        RAPIDPRO_URL="https://rp-test.com",
        RAPIDPRO_TOKEN="123",
        RAPIDPRO_TBCONNECT_FLOW="321",
    )
    def test_sync_low_risk(self):
        """
        Should not sync a low risk
        """
        profile = self.create_profile_and_check(risk=TBCheck.RISK_LOW)

        perform_sync_to_rapidpro()

        profile.refresh_from_db()

        self.assertFalse(profile.data["synced_to_tb_rapidpro"])

    def test_noop_without_settings(self):
        """
        Should not sync if rapidpro is not configured
        """
        profile = self.create_profile_and_check()
        perform_sync_to_rapidpro()

        profile.refresh_from_db()

        self.assertFalse(profile.data["synced_to_tb_rapidpro"])
