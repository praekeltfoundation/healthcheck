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

        admin = User.objects.create_superuser(
            username="testadmin", password="testadminpassword",
        )

        logger.info("Created superuser")

        self.client.login(
            username="testadmin", password="testadminpassword",
        )

        logger.info("Logged in with superuser")

        # a hack to get everything to work
        # NOTE:
        # TEST_REQUEST_DEFAULT_FORMAT must be set to `json`
        # otherwise FormData will be sent.
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {admin.auth_token}")

    def generate_data(self, hours=72):
        external_id = uuid4().hex
        timestamp = datetime.now() - timedelta(hours=hours)
        return {
            "msisdn": "+27820001001",
            "external_id": external_id,
            "timestamp": timestamp.isoformat(),
        }

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

        self.assertEqual(test_case.external_id, data.get("external_id"))

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

    def test_case_active(self):
        url = reverse("contacts:rest_confirmed_contact")

        # data_later -> is_active True
        data_later = self.generate_data(hours=10)
        # data_earlier -> is_active False
        data_earlier = self.generate_data(hours=12)

        r = self.client.post(url, data_later)
        self.assertEquals(r.status_code, 201)

        r2 = self.client.post(url, data=data_earlier)
        self.assertEquals(r2.status_code, 201)

        logger.info("Submitted two cases")

        case_earlier = Case.objects.filter(
            external_id=data_earlier.get("external_id")
        ).first()
        case_later = Case.objects.filter(
            external_id=data_later.get("external_id")
        ).first()

        self.assertIsNotNone(case_earlier)
        self.assertIsNotNone(case_later)

        test_contact = Contact.objects.filter(msisdn=data_earlier.get("msisdn")).first()

        self.assertIsNotNone(test_contact)

        self.assertEqual(case_earlier.contact, test_contact)
        self.assertEqual(case_earlier.contact, case_later.contact)

        self.assertFalse(case_earlier.is_active)
        self.assertTrue(case_later.is_active)

        logger.info("Finished testing two cases")
