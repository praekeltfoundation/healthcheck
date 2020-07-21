import logging
from datetime import datetime, timedelta
from uuid import uuid4

from django.test import Client, TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from users.models import User

from .models import Case, Contact

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


class AdminTest(TestCase):
    def setUp(self):
        self.client = Client()

        User.objects.create_superuser(
            username="testadmin", password="testadminpassword",
        )

        logger.info("Created superuser")

        self.client.login(
            username="testadmin", password="testadminpassword",
        )

        logger.info("Logged in with superuser")

        token = self.generate_user_token()

        # a hack to get everything to work
        # NOTE:
        # TEST_REQUEST_DEFAULT_FORMAT must be set to `json`
        # otherwise FormData will be sent.
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")

    def generate_data(self):
        external_id = uuid4().hex
        timestamp = datetime.now() + timedelta(days=3)
        return {
            "msisdn": "+27820001001",
            "external_id": external_id,
            "timestamp": timestamp.isoformat(),
        }

    def generate_user_token(self):
        url = "/admin/users/user/add/"

        data = {
            "username": "testuser",
            "password": "testuserpassword",
        }

        r = self.client.post(url, data=data)

        # admin user creation request returns 302
        self.assertEquals(r.status_code, 302)

        test_user = User.objects.get(username=data.get("username"))
        return test_user.auth_token

    def test_case_submittance(self):
        url = reverse("contacts:rest_confirmed_contact")

        data = self.generate_data()

        # first request returns 201
        r = self.client.post(url, data)
        self.assertEquals(r.status_code, 201)

        # second request returns 200
        r2 = self.client.post(url, data=data)
        self.assertEquals(r2.status_code, 200)

        logger.info("Submitted a case")

        test_case = Case.objects.filter(external_id=data.get("external_id")).first()

        self.assertIsNotNone(test_case)

        test_contact = Contact.objects.filter(msisdn=data.get("msisdn")).first()

        self.assertIsNotNone(test_contact)

        # check whether case is connected to proper contact
        self.assertEqual(test_case.contact, test_contact)

        # check all the fields for their default values
        self.assertTrue(test_case.is_active)

        # check if data is converted correctly
        # NOTE: `.replace(tzinfo=None)` has to be done
        # else validation fails
        self.assertEqual(
            test_case.date_start.replace(tzinfo=None),
            datetime.fromisoformat(data.get("timestamp")),
        )

        # check if enddate is calculated correctly
        self.assertEqual(
            test_case.date_end.replace(tzinfo=None),
            datetime.fromisoformat(data.get("timestamp")) + timedelta(days=14),
        )
