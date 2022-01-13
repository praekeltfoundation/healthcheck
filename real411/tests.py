from unittest.mock import MagicMock, patch

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from real411.models import Complaint
from real411.tasks import process_complaint_update


class ComplaintUpdateViewTests(APITestCase):
    url = reverse("update_complaint-list")
    complaint_data = {
        "complaint_ref": "REF001",
        "is_duplicate": False,
        "title": "test title",
        "overview": "test overview",
        "background_ruiling": "test background ruiling",
        "real411_backlink": "https://example.org",
        "status": {
            "id": 1,
            "code": "RES",
            "name": "Resolved",
            "description": "Complaint has been resolved",
        },
    }

    def setup_user(self):
        user = get_user_model().objects.create()
        permission = Permission.objects.get(codename="add_complaint")
        user.user_permissions.add(permission)
        self.client.force_login(user)
        return user

    def test_unauthorized(self):
        response = self.client.post(self.url, data={}, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_no_permission(self):
        user = get_user_model().objects.create()
        self.client.force_login(user)

        response = self.client.post(self.url, data={}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_invalid_body(self):
        self.setup_user()

        response = self.client.post(self.url, data={}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_missing_complaint(self):
        self.setup_user()

        response = self.client.post(self.url, data=self.complaint_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    @patch("real411.views.process_complaint_update")
    def test_valid_complaint(self, process_complaint_update: MagicMock):
        self.setup_user()
        Complaint.objects.create(complaint_ref="REF001", msisdn="+27820001001")

        response = self.client.post(self.url, data=self.complaint_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        process_complaint_update.delay.assert_called_once_with(self.complaint_data)


class ComplaintUpdateTaskTests(TestCase):
    @override_settings(RAPIDPRO_REAL411_FLOW="testflow")
    @patch("real411.tasks.rapidpro_client")
    def test_submit_to_rapidpro(self, rapidpro_client: MagicMock):
        Complaint.objects.create(complaint_ref="REF001", msisdn="+27820001001")
        process_complaint_update({"complaint_ref": "REF001"})
        rapidpro_client.create_flow_start.assert_called_once_with(
            "testflow",
            urns=["whatsapp:27820001001"],
            restart_participants=True,
            extra={"complaint_ref": "REF001"},
        )
