import responses
from django.test import TestCase, override_settings

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
            data={"donotreplace": "", "replaceint": 0, "replacebool": False},
        )
        profile = HealthCheckUserProfile(
            gender=TBCheck.GENDER_FEMALE,
            age=TBCheck.AGE_U18,
            location="+40.20361+40.20361",
            data={
                "donotreplace": "value",
                "replaceint": 1,
                "replacebool": True,
                "existing": "value",
            },
        )
        profile.update_from_tbcheck(tbCheck)
        self.assertEqual(profile.gender, TBCheck.GENDER_MALE)
        self.assertEqual(profile.age, TBCheck.AGE_18T40)
        self.assertEqual(profile.location, "+40.20361+40.20361")
        self.assertEqual(profile.language, "eng")
        self.assertEqual(
            profile.data,
            {
                "donotreplace": "value",
                "replaceint": 0,
                "replacebool": False,
                "existing": "value",
                "synced_to_tb_rapidpro": False,
                "follow_up_optin": True,
            },
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

    @responses.activate
    def test_update_tbconnect_group_arm(self):
        """
        Update tbconnect_group_arm with the first index arm
        """

        profile = HealthCheckUserProfile(
            msisdn="+27820001001",
            province="ZA-WC",
            city="JHB",
            research_consent=True,
            activation="tb_study_b",
        )
        profile.update_tbconnect_group_arm()

        self.assertIsNotNone(profile.tbconnect_group_arm)
        self.assertIsNotNone(profile.tbconnect_group_arm_timestamp)

    @responses.activate
    def test_update_tbconnect_group_arm_existing(self):
        """
        Not to update tbconnect_group_arm if already exist
        """

        profile = HealthCheckUserProfile(
            msisdn="+27820001001",
            province="ZA-WC",
            city="JHB",
            tbconnect_group_arm="connect",
        )
        profile.update_tbconnect_group_arm()

        self.assertEqual(profile.tbconnect_group_arm, "connect")
        self.assertIsNone(profile.tbconnect_group_arm_timestamp)

    @responses.activate
    def test_update_tbconnect_group_arm_disabled(self):
        """
        return none if activation is not tbstudy
        """

        profile = HealthCheckUserProfile(
            msisdn="+27820001001", province="ZA-WC", city="JHB"
        )
        profile.update_tbconnect_group_arm()

        self.assertIsNone(profile.tbconnect_group_arm)
        self.assertIsNone(profile.tbconnect_group_arm_timestamp)

    @responses.activate
    def test_update_tbconnect_group_arm_no_consent(self):
        """
        No to update group_arm if user did give research_consent
        """

        profile = HealthCheckUserProfile(
            msisdn="+27820001001", province="ZA-WC", city="JHB", research_consent=False
        )
        profile.update_tbconnect_group_arm()

        self.assertIsNone(profile.tbconnect_group_arm)
        self.assertIsNone(profile.tbconnect_group_arm_timestamp)

    @override_settings(SOFT_COMMITMENT_PLUS_LIMIT=0,)
    def test_get_tb_study_arms_forced_exclude(self):
        """
        Exclude soft commitment plus if setting is 0
        """
        profile = HealthCheckUserProfile(
            msisdn="+27820001001",
            province="ZA-WC",
            city="JHB",
            research_consent=True,
            activation="tb_study_c",
        )
        arms = profile._get_tb_study_arms()
        self.assertEqual(len(arms), 1)

    def test_get_tb_study_arms_include(self):
        """
        Include soft commitment plus if count is less than setting
        """
        profile = HealthCheckUserProfile(
            msisdn="+27820001001",
            province="ZA-WC",
            city="JHB",
            research_consent=True,
            activation="tb_study_c",
        )
        arms = profile._get_tb_study_arms()
        self.assertEqual(len(arms), 2)

    def test_get_tb_study_arms_exclude(self):
        """
        Exclude soft commitment plus if count is more than setting
        """
        for i in range(5):
            HealthCheckUserProfile.objects.create(
                msisdn=f"+2782000200{i}",
                research_consent=True,
                activation="tb_study_c",
                tbconnect_group_arm="soft_commitment_plus",
            )
        profile = HealthCheckUserProfile(
            msisdn="+27820001001",
            province="ZA-WC",
            city="JHB",
            research_consent=True,
            activation="tb_study_c",
        )
        arms = profile._get_tb_study_arms()
        self.assertEqual(len(arms), 1)

    @override_settings(SOFT_COMMITMENT_PLUS_LIMIT=10,)
    def test_get_tb_study_arms_include_soft_commit_plus(self):
        """
        Include soft commitment plus if setting is not 0
        """
        profile = HealthCheckUserProfile(
            msisdn="+27820001001",
            province="ZA-WC",
            city="JHB",
            research_consent=True,
            activation="tb_study_b",
        )
        arms = profile._get_tb_study_arms()
        self.assertEqual(len(arms), 2)

    def test_allow_null_province(self):
        """
        Exclude soft commitment plus if count is more than setting
        """
        profile = HealthCheckUserProfile(
            msisdn="+27820001001",
            province=None,
            city="JHB",
            research_consent=True,
            activation="tb_study_c"
        )

        self.assertIsNotNone(profile)

    def test_allow_blank_province(self):
        """
        Exclude soft commitment plus if count is more than setting
        """
        profile = HealthCheckUserProfile(
            msisdn="+27820001001",
            province="",
            city="JHB",
            research_consent=True,
            activation="tb_study_c"
        )

        self.assertIsNotNone(profile)
