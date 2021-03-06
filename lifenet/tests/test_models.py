from django.test import TestCase

from lifenet.models import LNCheck


class LNCheckTests(TestCase):
    def test_hashed_msisdn(self):
        check = LNCheck.objects.create(
            **{
                "msisdn": "+123",
                "cough": False,
                "fever": False,
                "sore_throat": False,
                "difficulty_breathing": False,
                "muscle_pain": True,
                "smell": True,
                "tracing": True,
            }
        )
        self.assertEqual(
            check.hashed_msisdn, "GyReRepLLYF5Ldr6IyA1mu8VM96Et16I0TFIyDvRmK4="
        )

    def test_get_processed_data(self):
        check = LNCheck.objects.create(
            **{
                "msisdn": "+123",
                "cough": False,
                "fever": False,
                "sore_throat": False,
                "difficulty_breathing": False,
                "tracing": True,
                "muscle_pain": True,
                "smell": True,
                "source": "Test",
                "age": LNCheck.Age.AGE_18T39,
                "exposure": LNCheck.Exposure.EXPOSURE_NOT_SURE,
                "risk": LNCheck.Risk.RISK_HIGH,
                "language": "eng",
            }
        )
        self.assertEqual(
            check.get_processed_data(),
            {
                "deduplication_id": str(check.deduplication_id),
                "msisdn": "GyReRepLLYF5Ldr6IyA1mu8VM96Et16I0TFIyDvRmK4=",
                "timestamp": check.timestamp.isoformat(),
                "source": "Test",
                "age": LNCheck.Age.AGE_18T39,
                "cough": False,
                "fever": False,
                "sore_throat": False,
                "difficulty_breathing": False,
                "muscle_pain": True,
                "smell": True,
                "exposure": LNCheck.Exposure.EXPOSURE_NOT_SURE,
                "risk": LNCheck.Risk.RISK_HIGH,
                "follow_up_optin": False,
                "language": "eng",
            },
        )
