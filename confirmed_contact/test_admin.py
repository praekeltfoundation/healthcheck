import io
from datetime import datetime

from django.contrib.auth.models import User
from django.test import TestCase
from django.utils.timezone import utc

from confirmed_contact.models import ConfirmedContact


class CsvImportTests(TestCase):
    def test_csv_import(self):
        """
        Importing a CSV should insert the objects into the database, with the username
        of the user who performed the import
        """
        User.objects.create_superuser("testuser", "test@example.org", "testpass")
        self.client.login(username="testuser", password="testpass")
        r = self.client.post(
            "/admin/confirmed_contact/confirmedcontact/import_csv/",
            {
                "csv_file": io.StringIO(
                    "\n".join(
                        [
                            "msisdn,timestamp",
                            "+27820001003,2020-05-15 15:17:57.803857Z",
                            "+27820001004,2020-05-15 15:17:58.803857Z",
                        ]
                    )
                )
            },
            follow=True,
        )

        [message] = r.context["messages"]
        self.assertEqual(message.message, "CSV import successful")

        [c1, c2] = ConfirmedContact.objects.order_by("msisdn").all()

        self.assertEqual(c1.msisdn, "+27820001003")
        self.assertEqual(
            c1.timestamp, datetime(2020, 5, 15, 15, 17, 57, 803857, tzinfo=utc)
        )
        self.assertEqual(c1.created_by, "testuser")

        self.assertEqual(c2.msisdn, "+27820001004")
        self.assertEqual(
            c2.timestamp, datetime(2020, 5, 15, 15, 17, 58, 803857, tzinfo=utc)
        )
        self.assertEqual(c2.created_by, "testuser")
