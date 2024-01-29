import logging
from datetime import datetime, timedelta

import pytz
import responses
from django.test import Client, TransactionTestCase
from django.urls import reverse
from rest_framework.test import APIClient

from contacts.models import Case, Contact
from contacts.tasks import send_contact_update
from users.models import User

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


class CaseTasksTests(TransactionTestCase):
    allow_database_queries = True

    def setUp(self):
        self.client = Client()

        admin = User.objects.create_superuser(
            username="testadmin",
            password="testadminpassword",
        )

        logger.info("Created superuser")

        self.client.login(
            username="testadmin",
            password="testadminpassword",
        )

        logger.info("Logged in with superuser")

        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {admin.auth_token}")

        self.data = {
            "external_id": "external_id",
            "date_start": (datetime.now() - timedelta(days=13)).replace(
                tzinfo=pytz.UTC
            ),
        }

        self.msisdn = "+27820001001".lstrip("+")
        self.contact = Contact.objects.create(msisdn=self.msisdn)
        self.case = Case.objects.create(**self.data)
        self.case.contact = self.contact
        self.case.save(update_fields=["contact"])
        logger.info("Created contact and case.")

    def test_expired_date(self):
        url = reverse("contacts:rest_confirmed_contact")

        self.client.post(
            url,
            data={
                "msisdn": "+27820001009",
                "external_id": "qwerty",
                "timestamp": datetime.now() - timedelta(days=20),
            },
        )

        expired_case = Case.objects.filter(external_id="qwerty").first()
        self.assertFalse(expired_case.is_active)

    @responses.activate
    def test_dates(self):
        logger.info("Started testing date_start")
        self.assertIsNone(self.case.date_notification_start)

        date_start_response = {
            "fields": {
                "birthday": None,
                "confirmed_contact": True,
                "healthcheck_completed": True,
                "language": None,
                "location": None,
                "name": None,
                "opted_in": False,
                "opted_in_at": None,
                "surname": None,
                "whatsapp_id": None,
                "whatsapp_profile_name": None,
            },
            "generation": 54,
            "schema": "1b09a076-fdfd-4a12-86fd-1408778d755d",
            "updated_at": "2020-08-02T18:40:13.562082Z",
        }

        responses.add(
            responses.PATCH,
            f"https://whatsapp.turn.io/v1/contacts/{self.msisdn}/profile",
            json=date_start_response,
            status=201,
        )

        result = send_contact_update(self.msisdn, True, self.case.id)

        self.case.refresh_from_db()

        self.assertIsNotNone(self.case.date_notification_start)
        self.assertTrue(
            self.case.date_notification_start <= datetime.now().replace(tzinfo=pytz.UTC)
        )

        # if tasks does return correct text - it has executed
        # without any issues
        self.assertEqual(
            result, f"Finished sending contact {True} update for {self.msisdn}."
        )

        # both dates are tested in same task since testing doesnt ensure correct order
        logger.info("Started testing date_end")

        self.assertIsNone(self.case.date_notification_end)

        date_start_response = {
            "fields": {
                "birthday": None,
                "confirmed_contact": False,
                "healthcheck_completed": True,
                "language": None,
                "location": None,
                "name": None,
                "opted_in": False,
                "opted_in_at": None,
                "surname": None,
                "whatsapp_id": None,
                "whatsapp_profile_name": None,
            },
            "generation": 54,
            "schema": "1b09a076-fdfd-4a12-86fd-1408778d755d",
            "updated_at": "2020-08-02T18:40:13.562082Z",
        }

        responses.add(
            responses.PATCH,
            f"https://whatsapp.turn.io/v1/contacts/{self.msisdn}/profile",
            json=date_start_response,
            status=201,
        )

        result = send_contact_update(self.msisdn, False, self.case.id)

        # local instance doesnt see celery performing updates
        self.case.refresh_from_db()

        # if tasks does return correct text - it has executed
        # without any issues
        self.assertEqual(
            result, f"Finished sending contact {False} update for {self.msisdn}."
        )

        self.assertIsNotNone(self.case.date_notification_end)
        self.assertTrue(
            self.case.date_notification_end <= datetime.now().replace(tzinfo=pytz.UTC)
        )
        self.assertTrue(
            self.case.date_notification_start <= self.case.date_notification_end
        )
