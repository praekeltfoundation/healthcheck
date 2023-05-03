from tbconnect.serializers import TBCheckCciDataSerializer
from django.test import TestCase
import responses


class TBCheckCciDataSerializerTest(TestCase):
    @responses.activate
    def test_missing_contact_number_validation(self):
        serializer = TBCheckCciDataSerializer(
            data={
                "name": "Tom",
                "language": "Eng",
                "tb_risk": "High",
                "responded": "No",
                "tb_tested": "Yes",
                "tb_test_results": "Yes",
                "screen_timeStamp": "2023-04-25 13:02:17",
            }
        )

        self.assertFalse(serializer.is_valid())
        self.assertEquals(serializer.errors, {"msisdn": ["This field is required."]})

    @responses.activate
    def test_missing_user_name_validation(self):
        serializer = TBCheckCciDataSerializer(
            data={
                "msisdn": "27821234567",
                "language": "Eng",
                "tb_risk": "High",
                "responded": "No",
                "tb_tested": "Yes",
                "tb_test_results": "Yes",
                "screen_timeStamp": "2023-04-25 13:02:17",
            }
        )

        self.assertTrue(serializer.is_valid())

    @responses.activate
    def test_none_value_user_name_validation(self):
        serializer = TBCheckCciDataSerializer(
            data={
                "msisdn": "27821234567",
                "name": None,
                "language": "Eng",
                "tb_risk": "High",
                "responded": "No",
                "tb_tested": "Yes",
                "tb_test_results": "Yes",
                "screen_timeStamp": "2023-04-25 13:02:17",
            }
        )

        self.assertTrue(serializer.is_valid())
