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
                "Opt_In": "True",
                "Drop_Off": "Yes",
                "TB_Test_Result_Desc": "Positive",
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
                "Opt_In": "False",
                "Drop_Off": "No",
                "TB_Test_Result_Desc": "Pending",
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
                "Opt_In": "True",
                "Drop_Off": "Yes",
                "TB_Test_Result_Desc": "Positive",
                "Screen_timeStamp": "2023-04-25 13:02:17",
            }
        )

        self.assertTrue(serializer.is_valid())

    @responses.activate
    def test_Optin_error_validation(self):
        serializer = TBCheckCciDataSerializer(
            data={
                "CLI": "27821234567",
                "Name": None,
                "Language": "Eng",
                "TB_Risk": "High",
                "Responded": "Yes",
                "TB_Tested": "Yes",
                "TB_Test_Results": "Yes",
                "Drop_Off": "Yes",
                "TB_Test_Result_Desc": "Positive",
                "Screen_timeStamp": "2023-09-04 13:02:17",
            }
        )

        self.assertFalse(serializer.is_valid())
        self.assertEquals(serializer.errors, {"Opt_In": ["This field is required."]})

    @responses.activate
    def test_drop_off_error_validation(self):
        serializer = TBCheckCciDataSerializer(
            data={
                "CLI": "27821234567",
                "Name": "Test",
                "Language": "Eng",
                "TB_Risk": "High",
                "Responded": "Yes",
                "TB_Tested": "Yes",
                "TB_Test_Results": "Yes",
                "Opt_In": "True",
                "TB_Test_Result_Desc": "Positive",
                "Screen_timeStamp": "2023-09-04 13:02:17",
            }
        )

        self.assertFalse(serializer.is_valid())
        self.assertEquals(serializer.errors, {"Drop_Off": ["This field is required."]})

    @responses.activate
    def test_result_description_validation(self):
        serializer = TBCheckCciDataSerializer(
            data={
                "CLI": "27821234567",
                "Name": "",
                "Language": "Eng",
                "TB_Risk": "High",
                "Responded": "Yes",
                "TB_Tested": "Yes",
                "TB_Test_Results": "Yes",
                "Opt_In": "True",
                "Drop_Off": "Yes",
                "Screen_timeStamp": "2023-09-05 13:02:17",
            }
        )

        self.assertFalse(serializer.is_valid())
        self.assertEquals(
            serializer.errors, {"TB_Test_Result_Desc": ["This field is required."]}
        )

    @responses.activate
    def test_optin_dropoff_results_validation(self):
        serializer = TBCheckCciDataSerializer(
            data={
                "CLI": "27821234567",
                "Name": None,
                "Language": "Eng",
                "TB_Risk": "High",
                "Responded": "Yes",
                "TB_Tested": "Yes",
                "TB_Test_Results": "Yes",
                "Opt_In": "True",
                "Drop_Off": "Yes",
                "TB_Test_Result_Desc": "Positive",
                "Screen_timeStamp": "2023-09-05 13:02:17",
            }
        )

        self.assertTrue(serializer.is_valid())
