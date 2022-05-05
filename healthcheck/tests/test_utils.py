from unittest.mock import Mock, patch

from django.test import TestCase

from healthcheck import utils
from selfswab.models import SelfSwabTest
from tbconnect.models import TBTest


class UtilsTests(TestCase):
    def test_hash_string(self):
        self.assertEqual(
            utils.hash_string("+27831231234"),
            "eIUHAUSFHvvZ2vpXxPJDwMZ2MuMPVpKOJHUeICFyQnE=",
        )

    def test_extract_reduced_accuracy_lat_long(self):
        lat, long = utils.extract_reduced_accuracy_lat_long("+40.20361+35.16361", 2)
        self.assertEqual(lat, 40.20)
        self.assertEqual(long, 35.16)

        lat, long = utils.extract_reduced_accuracy_lat_long("-40.20361-35.16361", 2)
        self.assertEqual(lat, -40.20)
        self.assertEqual(long, -35.16)

        lat, long = utils.extract_reduced_accuracy_lat_long("-40.20361+35.16361", 1)
        self.assertEqual(lat, -40.20)
        self.assertEqual(long, 35.2)

        lat, long = utils.extract_reduced_accuracy_lat_long("+40.20361-35.16361", 1)
        self.assertEqual(lat, 40.2)
        self.assertEqual(long, -35.2)

        lat, long = utils.extract_reduced_accuracy_lat_long("-40.20361+35.16361")
        self.assertEqual(lat, -40.20)
        self.assertEqual(long, 35.2)

        lat, long = utils.extract_reduced_accuracy_lat_long("+40.20361-35.16361")
        self.assertEqual(lat, 40.2)
        self.assertEqual(long, -35.2)

        lat, long = utils.extract_reduced_accuracy_lat_long(None)
        self.assertIsNone(lat)
        self.assertIsNone(long)

    def test_get_processed_records(self):
        test = TBTest.objects.create(
            **{"msisdn": "+123", "source": "test", "result": TBTest.RESULT_PENDING}
        )

        data = utils.get_processed_records(TBTest.objects.all())

        self.assertEqual(data, [test.get_processed_data()])

    @patch("healthcheck.utils.upload_to_bigquery")
    @patch("healthcheck.utils.get_latest_bigquery_timestamp")
    @patch("healthcheck.utils.get_bigquery_client")
    def test_sync_models_to_bigquery(
        self,
        mock_get_bigquery_client,
        mock_get_latest_bigquery_timestamp,
        mock_upload_to_bigquery,
    ):
        test = TBTest.objects.create(
            **{"msisdn": "+123", "source": "test", "result": TBTest.RESULT_PENDING}
        )

        dataset = "project123.tbconnect"

        fake_bigquery_client = Mock()
        mock_get_bigquery_client.return_value = fake_bigquery_client
        mock_get_latest_bigquery_timestamp.return_value = None

        models = {
            "tests": {
                "model": TBTest,
                "field": "updated_at",
                "fields": {"deduplication_id": "STRING"},
            },
        }

        utils.sync_models_to_bigquery("test_credentials.json", dataset, models)

        mock_get_latest_bigquery_timestamp.assert_called_with(
            fake_bigquery_client, dataset, "tests", "updated_at"
        )
        mock_upload_to_bigquery.assert_called_with(
            fake_bigquery_client,
            dataset,
            "tests",
            models["tests"]["fields"],
            [test.get_processed_data()],
        )

    @patch("healthcheck.utils.upload_to_bigquery")
    @patch("healthcheck.utils.get_latest_bigquery_timestamp")
    @patch("healthcheck.utils.get_bigquery_client")
    def test_sync_models_to_bigquery_with_filter(
        self,
        mock_get_bigquery_client,
        mock_get_latest_bigquery_timestamp,
        mock_upload_to_bigquery,
    ):
        SelfSwabTest.objects.create(
            **{
                "barcode": "111",
                "msisdn": "+123",
                "contact_id": "test1",
                "result": SelfSwabTest.Result.PENDING,
                "should_sync": False,
            }
        )
        test2 = SelfSwabTest.objects.create(
            **{
                "barcode": "222",
                "msisdn": "+124",
                "contact_id": "test2",
                "result": SelfSwabTest.Result.PENDING,
            }
        )

        dataset = "project123.selfswab"

        fake_bigquery_client = Mock()
        mock_get_bigquery_client.return_value = fake_bigquery_client
        mock_get_latest_bigquery_timestamp.return_value = None

        models = {
            "tests": {
                "model": SelfSwabTest,
                "field": "updated_at",
                "fields": {"id": "STRING"},
                "filter": {"key": "should_sync", "value": True},
            },
        }

        utils.sync_models_to_bigquery("test_credentials.json", dataset, models)

        mock_get_latest_bigquery_timestamp.assert_called_with(
            fake_bigquery_client, dataset, "tests", "updated_at"
        )
        mock_upload_to_bigquery.assert_called_with(
            fake_bigquery_client,
            dataset,
            "tests",
            models["tests"]["fields"],
            [test2.get_processed_data()],
        )
