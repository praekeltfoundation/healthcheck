from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from tbconnect.models import TBCheck, TBTest
from tbconnect.serializers import TBCheckSerializer
from userprofile.models import HealthCheckUserProfile
from userprofile.tests.test_views import BaseEventTestCase
from tbconnect.tests.test_utils import create_user_profile
import responses


class TBCheckViewSetTests(APITestCase, BaseEventTestCase):
    url = reverse("tbcheck-list")

    def test_data_validation(self):
        """
        The supplied data must be validated, and any errors returned
        """
        user = get_user_model().objects.create_user("test")
        user.user_permissions.add(Permission.objects.get(codename="add_tbcheck"))
        self.client.force_authenticate(user)
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_successful_request(self):
        """
        Should create a new TBCheck object in the database
        """
        user = get_user_model().objects.create_user("test")
        user.user_permissions.add(Permission.objects.get(codename="add_tbcheck"))
        self.client.force_authenticate(user)
        response = self.client.post(
            self.url,
            {
                "msisdn": "27856454612",
                "source": "USSD",
                "province": "ZA-WC",
                "city": "Cape Town",
                "age": TBCheck.AGE_18T40,
                "gender": TBCheck.GENDER_FEMALE,
                "cough": True,
                "fever": True,
                "sweat": False,
                "weight": True,
                "exposure": "yes",
                "tracing": True,
                "risk": TBCheck.RISK_LOW,
                "location": "+40.20361+40.20361",
                "follow_up_optin": True,
                "language": "eng",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        [tbcheck] = TBCheck.objects.all()
        self.assertEqual(tbcheck.msisdn, "27856454612")
        self.assertEqual(tbcheck.source, "USSD")
        self.assertEqual(tbcheck.province, "ZA-WC")
        self.assertEqual(tbcheck.city, "Cape Town")
        self.assertEqual(tbcheck.age, TBCheck.AGE_18T40)
        self.assertEqual(tbcheck.gender, TBCheck.GENDER_FEMALE)
        self.assertTrue(tbcheck.cough)
        self.assertTrue(tbcheck.fever)
        self.assertFalse(tbcheck.sweat)
        self.assertTrue(tbcheck.weight)
        self.assertEqual(tbcheck.exposure, "yes")
        self.assertTrue(tbcheck.tracing)
        self.assertEqual(tbcheck.risk, TBCheck.RISK_LOW)
        self.assertEqual(tbcheck.location, "+40.20361+40.20361")
        self.assertTrue(tbcheck.follow_up_optin)
        self.assertEqual(tbcheck.language, "eng")

    def test_location_validation(self):
        """
        Should create a new TBCheck object in the database
        """
        user = get_user_model().objects.create_user("test")
        user.user_permissions.add(Permission.objects.get(codename="add_tbcheck"))
        self.client.force_authenticate(user)
        response = self.client.post(
            self.url,
            {
                "msisdn": "27856454612",
                "source": "WhatsApp",
                "province": "ZA-WC",
                "city": "Cape Town",
                "age": TBCheck.AGE_18T40,
                "gender": TBCheck.GENDER_FEMALE,
                "cough": True,
                "fever": True,
                "sweat": False,
                "weight": True,
                "exposure": "yes",
                "tracing": True,
                "risk": TBCheck.RISK_LOW,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.json(),
            {"non_field_errors": ["location and city_location are both None"]},
        )

    def test_skip_location_validation(self):
        """
        Should create a new TBCheck object in the database
        """
        user = get_user_model().objects.create_user("test")
        user.user_permissions.add(Permission.objects.get(codename="add_tbcheck"))
        self.client.force_authenticate(user)
        response = self.client.post(
            self.url,
            {
                "msisdn": "27856454612",
                "source": "USSD",
                "province": "ZA-WC",
                "city": "Cape Town",
                "age": TBCheck.AGE_18T40,
                "gender": TBCheck.GENDER_FEMALE,
                "cough": True,
                "fever": True,
                "sweat": False,
                "weight": True,
                "exposure": "yes",
                "tracing": True,
                "risk": TBCheck.RISK_LOW,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_creates_user_profile(self):
        """
        The user profile should be created when the TB Check is saved
        """
        user = get_user_model().objects.create_user("test")
        user.user_permissions.add(Permission.objects.get(codename="add_tbcheck"))
        self.client.force_authenticate(user)
        response = self.client.post(
            self.url,
            {
                "msisdn": "+27856454612",
                "source": "USSD",
                "province": "ZA-WC",
                "city": "Cape Town",
                "age": TBCheck.AGE_18T40,
                "gender": TBCheck.GENDER_FEMALE,
                "cough": True,
                "fever": True,
                "sweat": False,
                "weight": True,
                "exposure": "yes",
                "tracing": True,
                "risk": TBCheck.RISK_LOW,
                "location": "+40.20361+40.20361",
            },
            format="json",
        )
        profile = HealthCheckUserProfile.objects.get(msisdn="+27856454612")
        self.assertEqual(profile.province, "ZA-WC")
        self.assertEqual(profile.city, "Cape Town")
        self.assertEqual(profile.age, TBCheck.AGE_18T40)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_commit_get_tested_update(self):
        """
        Update user profile commit field
        """
        user = get_user_model().objects.create_user("test")
        user.user_permissions.add(Permission.objects.get(codename="change_tbcheck"))
        self.client.force_authenticate(user)

        msisdn = "27831231234"
        tbcheck = TBCheck.objects.create(
            **{
                "msisdn": msisdn,
                "province": "ZA-GP",
                "city": "JHB",
                "cough": False,
                "fever": True,
                "sweat": False,
                "weight": True,
                "exposure": "yes",
                "tracing": True,
                "risk": TBCheck.RISK_LOW,
                "age": TBCheck.AGE_18T40,
                "gender": TBCheck.GENDER_FEMALE,
                "language": TBCheck.LANGUAGE_ZULU,
                "location": "+40.20361+40.20361",
            }
        )

        update_url = reverse("tbcheck-detail", args=(tbcheck.id,))
        response = self.client.patch(
            update_url,
            {
                "location": "+40.20361+40.20361",
                "city_location": "+40.20361+40.20361",
                "commit_get_tested": TBCheck.COMMIT_YES,
            },
        )

        self.assertEqual(tbcheck.msisdn, "27831231234")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        tbcheck.refresh_from_db()

        self.assertEqual(tbcheck.commit_get_tested, TBCheck.COMMIT_YES)

    def test_tbcheck_include_user_profile(self):
        """
        return profile when submitting tbcheck
        """
        user = get_user_model().objects.create_user("test")
        user.user_permissions.add(Permission.objects.get(codename="add_tbcheck"))
        self.client.force_authenticate(user)

        response = self.client.post(
            self.url,
            {
                "msisdn": "27856454612",
                "source": "USSD",
                "province": "ZA-WC",
                "city": "Cape Town",
                "age": TBCheck.AGE_18T40,
                "gender": TBCheck.GENDER_FEMALE,
                "cough": True,
                "fever": True,
                "sweat": False,
                "weight": True,
                "exposure": "yes",
                "tracing": True,
                "risk": TBCheck.RISK_LOW,
                "location": "+40.20361+40.20361",
                "follow_up_optin": True,
                "language": "eng",
            },
        )

        profile = response.json().get("profile", {})

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(profile.get("msisdn"), "27856454612")
        self.assertEqual(
            response.json().get("profile"),
            {
                "msisdn": "27856454612",
                "first_name": None,
                "last_name": None,
                "province": "ZA-WC",
                "city": "Cape Town",
                "age": "18-40",
                "date_of_birth": None,
                "gender": "female",
                "location": "+40.20361+40.20361",
                "city_location": None,
                "preexisting_condition": "",
                "rooms_in_household": None,
                "persons_in_household": None,
                "language": "eng",
                "data": {"follow_up_optin": True, "synced_to_tb_rapidpro": False},
                "tbconnect_group_arm": None,
                "research_consent": None,
                "originating_msisdn": None,
                "activation": None,
                "tbconnect_group_arm_timestamp": None,
            },
        )

    def test_creates_user_profile_with_group_arm(self):
        """
        Created user profile when the TB Check is saved with group arm
        """
        user = get_user_model().objects.create_user("test")
        user.user_permissions.add(Permission.objects.get(codename="add_tbcheck"))
        self.client.force_authenticate(user)
        self.client.post(
            self.url,
            {
                "msisdn": "+27856454612",
                "source": "USSD",
                "province": "ZA-WC",
                "city": "Cape Town",
                "age": TBCheck.AGE_18T40,
                "gender": TBCheck.GENDER_FEMALE,
                "cough": True,
                "fever": True,
                "sweat": False,
                "weight": True,
                "exposure": "yes",
                "tracing": True,
                "risk": TBCheck.RISK_HIGH,
                "location": "+40.20361+40.20361",
                "research_consent": True,
                "activation": "tb_study_a",
            },
            format="json",
        )
        profile = HealthCheckUserProfile.objects.get(msisdn="+27856454612")

        self.assertIsNotNone(profile.tbconnect_group_arm)

    def test_creates_user_profile_without_group_arm(self):
        """
        The user profile should be created when the TB Check is saved
        """
        user = get_user_model().objects.create_user("test")
        user.user_permissions.add(Permission.objects.get(codename="add_tbcheck"))
        self.client.force_authenticate(user)
        self.client.post(
            self.url,
            {
                "msisdn": "+27856454612",
                "source": "USSD",
                "province": "ZA-WC",
                "city": "Cape Town",
                "age": TBCheck.AGE_18T40,
                "gender": TBCheck.GENDER_FEMALE,
                "cough": True,
                "fever": True,
                "sweat": False,
                "weight": True,
                "exposure": "yes",
                "tracing": True,
                "risk": TBCheck.RISK_LOW,
                "location": "+40.20361+40.20361",
                "research_consent": True,
                "activation": "tb_study_a",
            },
            format="json",
        )
        profile = HealthCheckUserProfile.objects.get(msisdn="+27856454612")

        self.assertIsNone(profile.tbconnect_group_arm)


class TBTestViewSetTests(APITestCase, BaseEventTestCase):
    url = reverse("tbtest-list")

    def test_data_validation(self):
        """
        The supplied data must be validated, and any errors returned
        """
        user = get_user_model().objects.create_user("test")
        user.user_permissions.add(Permission.objects.get(codename="add_tbtest"))
        self.client.force_authenticate(user)
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_successful_create_request(self):
        """
        Should create a new TBTest object in the database
        """
        user = get_user_model().objects.create_user("test")
        user.user_permissions.add(Permission.objects.get(codename="add_tbtest"))
        self.client.force_authenticate(user)
        response = self.client.post(
            self.url,
            {
                "msisdn": "27856454612",
                "source": "WhatsApp",
                "result": TBTest.RESULT_PENDING,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        [tbtest] = TBTest.objects.all()
        self.assertEqual(tbtest.msisdn, "27856454612")
        self.assertEqual(tbtest.source, "WhatsApp")
        self.assertEqual(tbtest.result, TBTest.RESULT_PENDING)

    def test_successful_update_request(self):
        """
        Should create a new TBTest object in the database
        """
        tbtest = TBTest.objects.create(
            **{
                "msisdn": "27856454612",
                "source": "WhatsApp",
                "result": TBTest.RESULT_PENDING,
            }
        )

        user = get_user_model().objects.create_user("test")
        user.user_permissions.add(Permission.objects.get(codename="change_tbtest"))
        self.client.force_authenticate(user)
        update_url = reverse("tbtest-detail", args=(tbtest.id,))
        response = self.client.patch(update_url, {"result": TBTest.RESULT_POSITIVE})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        tbtest.refresh_from_db()
        self.assertEqual(tbtest.msisdn, "27856454612")
        self.assertEqual(tbtest.source, "WhatsApp")
        self.assertEqual(tbtest.result, TBTest.RESULT_POSITIVE)


class TBCheckSerializerTests(TestCase):
    def test_valid_tbcheck(self):
        """
        If age is <18 skip location and location_
        """
        data = {
            "msisdn": "+2349039756628",
            "source": "WhatsApp",
            "province": "ZA-GT",
            "city": "<not collected>",
            "age": "<18",
            "gender": "male",
            "cough": "True",
            "fever": "False",
            "sweat": "False",
            "weight": "False",
            "exposure": "no",
            "tracing": "False",
            "risk": "low",
        }
        serializer = TBCheckSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(
            dict(serializer.validated_data),
            {
                "age": "<18",
                "city": "<not collected>",
                "cough": True,
                "exposure": "no",
                "fever": False,
                "gender": "male",
                "msisdn": "+2349039756628",
                "province": "ZA-GT",
                "risk": "low",
                "source": "WhatsApp",
                "sweat": False,
                "tracing": False,
                "weight": False,
            },
        )


class TBResetViewSetTests(APITestCase):
    url = reverse("tbreset-detail", args=("+27856454612",))

    @override_settings(ALLOW_TB_RESET_MSISDNS=["+27820010001"],)
    def test_reset_not_allowed(self):
        """
        The supplied msisdn is not reset when not allowed.
        """
        user = get_user_model().objects.create_user("test")
        user.user_permissions.add(Permission.objects.get(codename="add_tbtest"))
        self.client.force_authenticate(user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @override_settings(ALLOW_TB_RESET_MSISDNS=["+27856454612"],)
    def test_reset_allowed(self):
        """
        The whitelisted msisdn is allowed to be reset.
        """
        HealthCheckUserProfile.objects.create(msisdn="+27856454612")
        user = get_user_model().objects.create_user("test")
        user.user_permissions.add(Permission.objects.get(codename="add_tbtest"))
        self.client.force_authenticate(user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TbCheckCciDataViewSetTest(APITestCase):
    url = reverse("tbcheckccidata-list")

    @responses.activate
    @override_settings(CCI_URL="https://cci-data-test.com")
    def test_cci_data_status_code(self):
        data = {
            "CLI": "27821234567",
            "Name": "Tom",
            "Language": "Eng",
            "TB_Risk": "High",
            "Responded": "No",
            "TB_Tested": "Yes",
            "TB_Test_Results": "Yes",
            "Opt_In": "Yes",
            "Drop_Off": "No",
            "TB_Test_Result_Desc": "Pending",
            "Screen_timeStamp": "2023-04-25 13:02:17"
        }

        create_user_profile("27821234567")
        response = self.client.post(self.url, data=data)

        self.assertEqual(response.status_code, 200)
