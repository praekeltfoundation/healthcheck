from tbconnect.serializers import TBCheckCciDataSerializer
from django.test import TestCase
import responses


class TBCheckCciDataSerializerTest(TestCase):
    @responses.activate
    def test_missing_contact_number_validation(self):
        serializer = TBCheckCciDataSerializer(
            data={
                "Name": None,
                "Language": "Eng",
                "TB_Risk": "High",
                "Responded": "Yes",
                "TB_Tested": "Yes",
                "TB_Test_Results": "Yes",
                "Screen_timeStamp": "2023-04-25 13:02:17",
            }
        )

        self.assertFalse(serializer.is_valid())
        self.assertEquals(serializer.errors, {"CLI": ["This field is required."]})

    @responses.activate
    def test_missing_user_name_validation(self):
        serializer = TBCheckCciDataSerializer(
            data={
                "CLI": "27821234567",
                "Language": "Eng",
                "TB_Risk": "High",
                "Responded": "Yes",
                "TB_Tested": "Yes",
                "TB_Test_Results": "Yes",
                "Screen_timeStamp": "2023-04-25 13:02:17",
            }
        )

        self.assertTrue(serializer.is_valid())

    @responses.activate
    def test_none_value_user_name_validation(self):
        serializer = TBCheckCciDataSerializer(
            data={
                "CLI": "27821234567",
                "Name": None,
                "Language": "Eng",
                "TB_Risk": "High",
                "Responded": "Yes",
                "TB_Tested": "Yes",
                "TB_Test_Results": "Yes",
                "Screen_timeStamp": "2023-04-25 13:02:17",
            }
        )

        self.assertTrue(serializer.is_valid())
