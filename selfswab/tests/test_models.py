from django.test import TestCase
from django.utils import timezone

from selfswab.models import SelfSwabScreen, SelfSwabTest


class SelfSwabTestTests(TestCase):
    def test_hashed_msisdn(self):
        test = SelfSwabTest.objects.create(**{"msisdn": "+123"})
        self.assertEqual(
            test.hashed_msisdn, "GyReRepLLYF5Ldr6IyA1mu8VM96Et16I0TFIyDvRmK4="
        )

    def test_get_processed_data(self):
        collection_timestamp = timezone.now()
        test = SelfSwabTest.objects.create(
            **{"msisdn": "+123", "collection_timestamp": collection_timestamp}
        )

        self.assertEqual(
            test.get_processed_data(),
            {
                "id": str(test.id),
                "contact_id": test.contact_id,
                "msisdn": "GyReRepLLYF5Ldr6IyA1mu8VM96Et16I0TFIyDvRmK4=",
                "result": SelfSwabTest.RESULT_PENDING,
                "barcode": test.barcode,
                "timestamp": test.timestamp.isoformat(),
                "updated_at": test.updated_at.isoformat(),
                "collection_timestamp": collection_timestamp.isoformat(),
                "received_timestamp": None,
                "authorized_timestamp": None,
            },
        )

    def test_set_result(self):
        test = SelfSwabTest.objects.create(**{"msisdn": "+123"})

        test.set_result("POS")
        self.assertEqual(test.result, SelfSwabTest.RESULT_POSITIVE)
        test.set_result("Positive")
        self.assertEqual(test.result, SelfSwabTest.RESULT_POSITIVE)
        test.set_result("DETECTED")
        self.assertEqual(test.result, SelfSwabTest.RESULT_POSITIVE)
        test.set_result("NOT DET")
        self.assertEqual(test.result, SelfSwabTest.RESULT_NEGATIVE)
        test.set_result("NOT DETECTED")
        self.assertEqual(test.result, SelfSwabTest.RESULT_NEGATIVE)
        test.set_result("INV")
        self.assertEqual(test.result, SelfSwabTest.RESULT_INVALID)
        test.set_result("REJ")
        self.assertEqual(test.result, SelfSwabTest.RESULT_REJECTED)
        test.set_result("EQV")
        self.assertEqual(test.result, SelfSwabTest.RESULT_EQUIVOCAL)
        test.set_result("INCON")
        self.assertEqual(test.result, SelfSwabTest.RESULT_INCONCLUSIVE)
        test.set_result("INDETERMINATE")
        self.assertEqual(test.result, SelfSwabTest.RESULT_INDETERMINATE)
        test.set_result("Error")
        self.assertEqual(test.result, SelfSwabTest.RESULT_ERROR)


class SelfSwabScreenTests(TestCase):
    def test_hashed_msisdn(self):
        screen = SelfSwabScreen.objects.create(
            **{
                "msisdn": "+123",
                "cough": True,
                "fever": True,
                "shortness_of_breath": True,
                "body_aches": True,
                "loss_of_taste_smell": True,
                "sore_throat": True,
                "additional_symptoms": True,
            }
        )
        self.assertEqual(
            screen.hashed_msisdn, "GyReRepLLYF5Ldr6IyA1mu8VM96Et16I0TFIyDvRmK4="
        )

    def test_get_processed_data(self):
        screen = SelfSwabScreen.objects.create(
            **{
                "contact_id": "123",
                "msisdn": "+123",
                "age": SelfSwabScreen.Age.FROM_18_TO_40,
                "gender": SelfSwabScreen.Gender.FEMALE,
                "facility": "Test",
                "risk_type": SelfSwabScreen.HIGH_RISK,
                "cough": True,
                "fever": True,
                "shortness_of_breath": True,
                "body_aches": True,
                "loss_of_taste_smell": True,
                "sore_throat": True,
                "additional_symptoms": True,
                "occupation": "Doctor",
                "employee_number": "emp-123",
                "pre_existing_condition": "diabetes",
            }
        )
        self.assertEqual(
            screen.get_processed_data(),
            {
                "id": str(screen.id),
                "contact_id": screen.contact_id,
                "msisdn": "GyReRepLLYF5Ldr6IyA1mu8VM96Et16I0TFIyDvRmK4=",
                "timestamp": screen.timestamp.isoformat(),
                "age": SelfSwabScreen.Age.FROM_18_TO_40,
                "gender": SelfSwabScreen.Gender.FEMALE,
                "facility": "Test",
                "risk_type": SelfSwabScreen.HIGH_RISK,
                "cough": True,
                "fever": True,
                "shortness_of_breath": True,
                "body_aches": True,
                "loss_of_taste_smell": True,
                "sore_throat": True,
                "additional_symptoms": True,
                "occupation": "Doctor",
                "employee_number": "MDJ3NWxchSKulLh+Hrn2RldM8hM1S5hBTWgeO/mAaZI=",
                "pre_existing_condition": "diabetes",
            },
        )
