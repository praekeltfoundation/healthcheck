import datetime
import json

import responses
from django.test import TestCase, override_settings
from django.conf import settings

from userprofile import tasks


def override_get_today():
    return datetime.datetime.strptime("20200117", "%Y%m%d").date()


class MarkTurnContactHealthCheckCompleteTests(TestCase):
    @override_settings(API_URL=None, TURN_API_KEY=None)
    @responses.activate
    def test_skips_when_no_settings(self):
        """
        Should not send anything if the settings aren't set
        """
        tasks.mark_turn_contact_healthcheck_complete("+27820001001")
        self.assertEqual(len(responses.calls), 0)

    @override_settings(API_URL="https://turn", TURN_API_TOKEN="token")
    @responses.activate
    def test_send_successful(self):
        """
        Should send with correct request data
        """
        responses.add(
            responses.PATCH,
            "https://turn/v1/contacts/27820001001/profile",
            json={},  # noqa: F821
        )
        tasks.mark_turn_contact_healthcheck_complete("+27820001001")
        [call] = responses.calls
        self.assertEqual(json.loads(call.request.body), {"healthcheck_completed": True})
        self.assertEqual(
            call.request.headers["Authorization"], f"Bearer {settings.TURN_API_KEY}"
        )
        self.assertEqual(call.request.headers["Accept"], "application/vnd.v1+json")
