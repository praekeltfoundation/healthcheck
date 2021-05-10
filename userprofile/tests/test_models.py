from django.test import TestCase, override_settings
from unittest.mock import patch, call, ANY

from tbconnect.models import TBCheck
from userprofile.models import Covid19Triage, HealthCheckUserProfile


class HealthCheckUserProfileTests(TestCase):
    def test_update_from_healthcheck(self):
        """
        Updates the correct fields from the healthcheck
        """
        healthcheck = Covid19Triage(
            msisdn="+27820001001",
            first_name="first",
            last_name=None,
            data={"donotreplace": "", "replaceint": 0, "replacebool": False},
        )
        profile = HealthCheckUserProfile(
            first_name="oldfirst",
            last_name="old_last",
            data={
                "donotreplace": "value",
                "replaceint": 1,
                "replacebool": True,
                "existing": "value",
            },
        )
        profile.update_from_healthcheck(healthcheck)
        self.assertEqual(profile.first_name, "first")
        self.assertEqual(profile.last_name, "old_last")
        self.assertEqual(
            profile.data,
            {
                "donotreplace": "value",
                "replaceint": 0,
                "replacebool": False,
                "existing": "value",
            },
        )

    def test_update_from_tbcheck(self):
        """
        Updates the correct fields from the TB Check
        """
        tbCheck = TBCheck(
            msisdn="+27820001001",
            gender=TBCheck.GENDER_MALE,
            age=TBCheck.AGE_18T40,
            location=None,
            follow_up_optin=True,
            language="eng",
        )
        profile = HealthCheckUserProfile(
            gender=TBCheck.GENDER_FEMALE,
            age=TBCheck.AGE_U18,
            location="+40.20361+40.20361",
        )
        profile.update_from_tbcheck(tbCheck)
        self.assertEqual(profile.gender, TBCheck.GENDER_MALE)
        self.assertEqual(profile.age, TBCheck.AGE_18T40)
        self.assertEqual(profile.location, "+40.20361+40.20361")
        self.assertEqual(profile.language, "eng")
        self.assertEqual(
            profile.data, {"follow_up_optin": True, "synced_to_tb_rapidpro": False},
        )

    def test_get_or_prefill_existing(self):
        """
        Returns existing profile
        """
        profile = HealthCheckUserProfile.objects.create(msisdn="+27820001001")
        fetched_profile = HealthCheckUserProfile.objects.get_or_prefill("+27820001001")
        self.assertEqual(profile.msisdn, fetched_profile.msisdn)

    def test_get_or_prefill_no_values(self):
        """
        Should return an empty profile if there are matching profiles, and no data to
        prefill with
        """
        profile = HealthCheckUserProfile.objects.get_or_prefill("+27820001001")
        self.assertEqual(profile.msisdn, "")

    def test_get_or_prefill_existing_healthchecks(self):
        """
        If no profile exists, and there are existing healthchecks, should use those to
        prefill the profile
        """
        Covid19Triage.objects.create(
            msisdn="+27820001001",
            first_name="oldfirst",
            last_name="oldlast",
            fever=False,
            cough=False,
            sore_throat=False,
            tracing=True,
        )
        Covid19Triage.objects.create(
            msisdn="+27820001001",
            last_name="newlast",
            fever=False,
            cough=False,
            sore_throat=False,
            tracing=True,
            preexisting_condition="no",
        )
        profile = HealthCheckUserProfile.objects.get_or_prefill("+27820001001")
        self.assertEqual(profile.first_name, "oldfirst")
        self.assertEqual(profile.last_name, "newlast")
        self.assertEqual(profile.preexisting_condition, "no")

    @patch("userprofile.models.update_turn_contact")
    def test_update_post_screening_study_arms(self, mock_update_turn_contact):
        profile = HealthCheckUserProfile(
            msisdn="+27820001001",
            first_name="oldfirst",
            last_name="old_last",
            data={
                "donotreplace": "value",
                "replaceint": 1,
                "replacebool": True,
                "existing": "value",
            },
        )

        profile.update_post_screening_study_arms()

        self.assertIsNotNone(profile.hcs_study_a_arm)
        self.assertIsNotNone(profile.hcs_study_c_arm)

        mock_update_turn_contact.delay.assert_has_calls(
            [
                call("+27820001001", "hcs_study_a_arm", profile.hcs_study_a_arm),
                call("+27820001001", "hcs_study_c_arm", profile.hcs_study_c_arm),
            ]
        )

    @patch("userprofile.models.update_turn_contact")
    def test_update_post_screening_study_arms_populated(self, mock_update_turn_contact):
        profile = HealthCheckUserProfile(
            msisdn="+27820001001",
            first_name="oldfirst",
            last_name="old_last",
            hcs_study_a_arm=HealthCheckUserProfile.StudyArm.CONTROL,
            hcs_study_c_arm=HealthCheckUserProfile.StudyArm.CONTROL,
            data={
                "donotreplace": "value",
                "replaceint": 1,
                "replacebool": True,
                "existing": "value",
            },
        )

        profile.update_post_screening_study_arms()

        mock_update_turn_contact.delay.assert_not_called()

    @patch("userprofile.models.update_turn_contact")
    @override_settings(HCS_STUDY_A_ACTIVE=False, HCS_STUDY_C_ACTIVE=False)
    def test_update_post_screening_study_arms_deactivated(
        self, mock_update_turn_contact
    ):
        profile = HealthCheckUserProfile(
            msisdn="+27820001001",
            first_name="oldfirst",
            last_name="old_last",
            data={
                "donotreplace": "value",
                "replaceint": 1,
                "replacebool": True,
                "existing": "value",
            },
        )

        profile.update_post_screening_study_arms()

        self.assertIsNone(profile.hcs_study_a_arm)
        self.assertIsNone(profile.hcs_study_c_arm)

        mock_update_turn_contact.delay.assert_not_called()
