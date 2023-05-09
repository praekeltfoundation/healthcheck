import json

import responses
from django.test import TestCase, override_settings
from django.utils import timezone

from tbconnect.models import TBCheck
from tbconnect.tasks import (
    perform_sync_to_rapidpro,
    send_tbcheck_data_to_cci,
    get_user_profile,
)
from userprofile.models import HealthCheckUserProfile
from tbconnect.tests.test_utils import create_user_profile


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
        activation=None,
        tbconnect_group_arm=None,
        commit_get_tested=None,
    ):
        TBCheck.objects.create(
            **{
                "msisdn": msisdn,
                "cough": True,
                "fever": True,
                "sweat": True,
                "weight": True,
                "tracing": True,
                "source": source,
                "exposure": TBCheck.EXPOSURE_YES,
                "completed_timestamp": self.completed_timestamp,
                "risk": risk,
                "follow_up_optin": optin,
                "activation": activation,
                "commit_get_tested": commit_get_tested,
            }
        )

        return HealthCheckUserProfile.objects.create(
            **{
                "msisdn": msisdn,
                "language": "eng",
                "data": {"follow_up_optin": optin, "synced_to_tb_rapidpro": synced},
                "tbconnect_group_arm": tbconnect_group_arm,
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
        Should sync a profile created from WhatsApp, if not synced before
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

        [call1, call2] = responses.calls
        body = json.loads(call1.request.body)
        self.assertEqual(
            body,
            {
                "flow": "321",
                "urns": ["whatsapp:27830000001"],
                "extra": {
                    "risk": "high",
                    "source": "WhatsApp",
                    "follow_up_optin": True,
                    "completed_timestamp": self.completed_timestamp.strftime(
                        "%d/%m/%Y"
                    ),
                    "exposure": TBCheck.EXPOSURE_YES,
                    "language": "eng",
                    "activation": None,
                    "tbconnect_group_arm": None,
                    "tbconnect_group_arm_timestamp": None,
                    "commit_get_tested": None,
                    "research_consent": None,
                },
            },
        )
        body = json.loads(call2.request.body)
        self.assertEqual(
            body,
            {
                "flow": "321",
                "urns": ["whatsapp:27830000002"],
                "extra": {
                    "risk": "high",
                    "source": "WhatsApp",
                    "follow_up_optin": False,
                    "completed_timestamp": self.completed_timestamp.strftime(
                        "%d/%m/%Y"
                    ),
                    "exposure": TBCheck.EXPOSURE_YES,
                    "language": "eng",
                    "activation": None,
                    "tbconnect_group_arm": None,
                    "tbconnect_group_arm_timestamp": None,
                    "commit_get_tested": None,
                    "research_consent": None,
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
                    "follow_up_optin": True,
                    "completed_timestamp": self.completed_timestamp.strftime(
                        "%d/%m/%Y"
                    ),
                    "exposure": TBCheck.EXPOSURE_YES,
                    "language": "eng",
                    "activation": None,
                    "tbconnect_group_arm": None,
                    "tbconnect_group_arm_timestamp": None,
                    "commit_get_tested": None,
                    "research_consent": None,
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
        Should sync low risk
        """
        profile = self.create_profile_and_check(risk=TBCheck.RISK_LOW)

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
                    "risk": "low",
                    "source": "WhatsApp",
                    "follow_up_optin": True,
                    "completed_timestamp": self.completed_timestamp.strftime(
                        "%d/%m/%Y"
                    ),
                    "exposure": TBCheck.EXPOSURE_YES,
                    "language": "eng",
                    "activation": None,
                    "tbconnect_group_arm": None,
                    "tbconnect_group_arm_timestamp": None,
                    "commit_get_tested": None,
                    "research_consent": None,
                },
            },
        )

    @responses.activate
    @override_settings(
        RAPIDPRO_URL="https://rp-test.com",
        RAPIDPRO_TOKEN="123",
        RAPIDPRO_TBCONNECT_FLOW="321",
    )
    def test_sync_whatsapp_agent(self):
        """
        Should sync a profile created from WhatsApp via shared agent device,
        if not synced before
        """
        profile = self.create_profile_and_check(activation="tb_soccer_1_agent")

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
                    "source": "WhatsApp",
                    "follow_up_optin": True,
                    "completed_timestamp": self.completed_timestamp.strftime(
                        "%d/%m/%Y"
                    ),
                    "exposure": TBCheck.EXPOSURE_YES,
                    "language": "eng",
                    "activation": "tb_soccer_1_agent",
                    "tbconnect_group_arm": None,
                    "tbconnect_group_arm_timestamp": None,
                    "commit_get_tested": None,
                    "research_consent": None,
                },
            },
        )

    def test_noop_without_settings(self):
        """
        Should not sync if rapidpro is not configured
        """
        profile = self.create_profile_and_check()
        perform_sync_to_rapidpro()

        profile.refresh_from_db()

        self.assertFalse(profile.data["synced_to_tb_rapidpro"])

    @responses.activate
    @override_settings(
        RAPIDPRO_URL="https://rp-test.com",
        RAPIDPRO_TOKEN="123",
        RAPIDPRO_TBCONNECT_FLOW="321",
    )
    def test_sync_whatsapp_to_rapidpro(self):
        """
        Should sync a profile created from WhatsApp including a study,
        if not synced before
        """
        profile = self.create_profile_and_check()
        self.create_profile_and_check(
            msisdn="+27830000004",
            tbconnect_group_arm="soft_commitment",
            commit_get_tested="yes",
        )

        responses.add(
            responses.POST,
            f"https://rp-test.com/api/v2/flow_starts.json",
            json=self.flow_response,
        )

        perform_sync_to_rapidpro()

        profile.refresh_from_db()
        self.assertTrue(profile.data["synced_to_tb_rapidpro"])

        [call1, call2] = responses.calls
        body = json.loads(call1.request.body)
        self.assertEqual(
            body,
            {
                "flow": "321",
                "urns": ["whatsapp:27830000001"],
                "extra": {
                    "risk": "high",
                    "source": "WhatsApp",
                    "follow_up_optin": True,
                    "completed_timestamp": self.completed_timestamp.strftime(
                        "%d/%m/%Y"
                    ),
                    "exposure": TBCheck.EXPOSURE_YES,
                    "language": "eng",
                    "activation": None,
                    "tbconnect_group_arm": None,
                    "tbconnect_group_arm_timestamp": None,
                    "commit_get_tested": None,
                    "research_consent": None,
                },
            },
        )
        body = json.loads(call2.request.body)
        self.assertEqual(
            body,
            {
                "flow": "321",
                "urns": ["whatsapp:27830000004"],
                "extra": {
                    "risk": "high",
                    "source": "WhatsApp",
                    "follow_up_optin": True,
                    "completed_timestamp": self.completed_timestamp.strftime(
                        "%d/%m/%Y"
                    ),
                    "exposure": TBCheck.EXPOSURE_YES,
                    "language": "eng",
                    "activation": None,
                    "tbconnect_group_arm": "soft_commitment",
                    "tbconnect_group_arm_timestamp": None,
                    "commit_get_tested": "yes",
                    "research_consent": None,
                },
            },
        )

    @responses.activate
    @override_settings(
        RAPIDPRO_URL="https://rp-test.com",
        RAPIDPRO_TOKEN="123",
        RAPIDPRO_TBCONNECT_FLOW="321",
    )
    def test_sync_ussd_to_rapidpro(self):
        """
        Should sync a profile created from WhatsApp including a study,
        if not synced before
        """
        profile = self.create_profile_and_check()
        self.create_profile_and_check(
            msisdn="+27830000003",
            source="USSD",
            tbconnect_group_arm="control",
            commit_get_tested=None,
        )

        responses.add(
            responses.POST,
            f"https://rp-test.com/api/v2/flow_starts.json",
            json=self.flow_response,
        )

        perform_sync_to_rapidpro()

        profile.refresh_from_db()
        self.assertTrue(profile.data["synced_to_tb_rapidpro"])

        [call1, call2] = responses.calls
        body = json.loads(call1.request.body)
        self.assertEqual(
            body,
            {
                "flow": "321",
                "urns": ["whatsapp:27830000001"],
                "extra": {
                    "risk": "high",
                    "source": "WhatsApp",
                    "follow_up_optin": True,
                    "completed_timestamp": self.completed_timestamp.strftime(
                        "%d/%m/%Y"
                    ),
                    "exposure": TBCheck.EXPOSURE_YES,
                    "language": "eng",
                    "activation": None,
                    "tbconnect_group_arm": None,
                    "tbconnect_group_arm_timestamp": None,
                    "commit_get_tested": None,
                    "research_consent": None,
                },
            },
        )
        body = json.loads(call2.request.body)
        self.assertEqual(
            body,
            {
                "flow": "321",
                "urns": ["tel:+27830000003"],
                "extra": {
                    "risk": "high",
                    "source": "USSD",
                    "follow_up_optin": True,
                    "completed_timestamp": self.completed_timestamp.strftime(
                        "%d/%m/%Y"
                    ),
                    "exposure": TBCheck.EXPOSURE_YES,
                    "language": "eng",
                    "activation": None,
                    "tbconnect_group_arm": "control",
                    "tbconnect_group_arm_timestamp": None,
                    "commit_get_tested": None,
                    "research_consent": None,
                },
            },
        )


class SendUserDataToCCITests(TestCase):
    msisdn = "2781234567"

    def test_get_user_profile_data(self):
        profile = create_user_profile(self.msisdn)
        response = get_user_profile(self.msisdn)

        self.assertIsNotNone(response)
        self.assertEqual(response.msisdn, "2781234567")
        self.assertEqual(profile.province, response.province)

    def test_get_none_existing_user_profile_data(self):
        response = get_user_profile(self.msisdn)

        self.assertIsNone(response)

    @responses.activate
    @override_settings(CCI_URL="https://cci-data-test.com")
    def test_send_data_to_cci(self):
        data = {
            "CLI": self.msisdn,
            "Name": "Tom",
            "Language": "Eng",
            "TB_Risk": "High",
            "Responded": "Yes",
            "TB_Tested": "Yes",
            "TB_Test_Results": "Yes",
            "Screen_timeStamp": "2023-04-25 13:02:17",
        }

        responses.add(
            responses.POST,
            url="https://cci-data-test.com",
            body=b'"Received Sucessfully"',
            status=200,
        )

        create_user_profile(self.msisdn)
        response = send_tbcheck_data_to_cci(data)

        [resp] = responses.calls

        self.assertEquals(response, "CCI data submitted successfully")
        self.assertEqual(resp.response.content, b'"Received Sucessfully"')
        self.assertEqual(resp.request.url, "https://cci-data-test.com/")

    @responses.activate
    @override_settings(CCI_URL="https://cci-data-test.com")
    def test_send_data_error_message_invalid_contact(self):
        data = {
            "CLI": self.msisdn,
            "Name": "Tom",
            "Language": "Eng",
            "TB_Risk": "High",
            "Responded": "Yes",
            "TB_Tested": "Yes",
            "TB_Test_Results": "Yes",
            "Screen_timeStamp": "2023-04-25 13:02:17",
        }

        responses.add(responses.POST, "https://cci-data-test.com", json=data)

        with self.assertRaises(Exception):
            send_tbcheck_data_to_cci(data)
