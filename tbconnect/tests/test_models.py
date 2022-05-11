from django.test import TestCase

from tbconnect.models import TBCheck, TBTest


class TBTestTests(TestCase):
    def test_hashed_msisdn(self):
        test = TBTest.objects.create(**{"msisdn": "+123"})
        self.assertEqual(
            test.hashed_msisdn, "GyReRepLLYF5Ldr6IyA1mu8VM96Et16I0TFIyDvRmK4="
        )

    def test_get_processed_data(self):
        test = TBTest.objects.create(
            **{"msisdn": "+123", "result": TBTest.RESULT_PENDING, "source": "Test"}
        )

        self.assertEqual(
            test.get_processed_data(),
            {
                "deduplication_id": str(test.deduplication_id),
                "msisdn": "GyReRepLLYF5Ldr6IyA1mu8VM96Et16I0TFIyDvRmK4=",
                "result": TBTest.RESULT_PENDING,
                "source": "Test",
                "timestamp": test.timestamp.isoformat(),
                "updated_at": test.updated_at.isoformat(),
            },
        )


class TBCheckTests(TestCase):
    def test_hashed_msisdn(self):
        check = TBCheck.objects.create(
            **{
                "msisdn": "+123",
                "cough": False,
                "fever": False,
                "sweat": False,
                "weight": False,
                "tracing": True,
            }
        )
        self.assertEqual(
            check.hashed_msisdn, "GyReRepLLYF5Ldr6IyA1mu8VM96Et16I0TFIyDvRmK4="
        )

    def test_get_processed_data(self):
        check = TBCheck.objects.create(
            **{
                "msisdn": "+123",
                "cough": False,
                "fever": False,
                "sweat": False,
                "weight": False,
                "tracing": True,
                "source": "Test",
                "age": TBCheck.AGE_18T40,
                "gender": TBCheck.GENDER_NOT_SAY,
                "exposure": TBCheck.EXPOSURE_NOT_SURE,
                "risk": TBCheck.RISK_HIGH,
                "language": "eng",
                "province": "ZA-WC",
            }
        )
        self.assertEqual(
            check.get_processed_data(),
            {
                "deduplication_id": str(check.deduplication_id),
                "msisdn": "GyReRepLLYF5Ldr6IyA1mu8VM96Et16I0TFIyDvRmK4=",
                "timestamp": check.timestamp.isoformat(),
                "source": "Test",
                "age": TBCheck.AGE_18T40,
                "gender": TBCheck.GENDER_NOT_SAY,
                "location_latitude": None,
                "location_longitude": None,
                "city_latitude": None,
                "city_longitude": None,
                "cough": False,
                "fever": False,
                "sweat": False,
                "weight": False,
                "exposure": TBCheck.EXPOSURE_NOT_SURE,
                "risk": TBCheck.RISK_HIGH,
                "follow_up_optin": False,
                "language": "eng",
                "province": "ZA-WC",
            },
        )
