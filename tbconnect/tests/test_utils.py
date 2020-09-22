from django.test import TestCase

from tbconnect import utils
from tbconnect.models import TBTest


class UtilsTests(TestCase):
    def test_hash_string(self):
        self.assertEqual(
            utils.hash_string("+27831231234"),
            "eIUHAUSFHvvZ2vpXxPJDwMZ2MuMPVpKOJHUeICFyQnE=",
        )

    def test_extract_lat_long(self):
        lat, long = utils.extract_lat_long("+40.20361+40.20361")
        self.assertEqual(lat, 40.20361)
        self.assertEqual(long, 40.20361)

        lat, long = utils.extract_lat_long(None)
        self.assertIsNone(lat)
        self.assertIsNone(long)

    def test_get_processed_records(self):
        test = TBTest.objects.create(
            **{"msisdn": "+123", "source": "test", "result": TBTest.RESULT_PENDING}
        )

        data = utils.get_processed_records(TBTest.objects.all())

        self.assertEqual(data, [test.get_processed_data()])
