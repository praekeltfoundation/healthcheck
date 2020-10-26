from django.test import TestCase

from selfswab.models import SelfSwabScreen, SelfSwabTest


class SelfSwabTestTests(TestCase):
    def test_hashed_msisdn(self):
        test = SelfSwabTest.objects.create(**{"msisdn": "+123"})
        self.assertEqual(
            test.hashed_msisdn, "GyReRepLLYF5Ldr6IyA1mu8VM96Et16I0TFIyDvRmK4="
        )

    def test_get_processed_data(self):
        test = SelfSwabTest.objects.create(
            **{"msisdn": "+123", "result": SelfSwabTest.RESULT_PENDING}
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
            },
        )


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
                "age": SelfSwabScreen.AGE_18T40,
                "gender": SelfSwabScreen.GENDER_NOT_SAY,
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
                "age": SelfSwabScreen.AGE_18T40,
                "gender": SelfSwabScreen.GENDER_NOT_SAY,
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
