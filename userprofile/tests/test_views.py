from urllib.parse import urlencode

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from userprofile.models import Covid19Triage, HealthCheckUserProfile


class BaseEventTestCase(object):
    def test_authentication_required(self):
        """
        There must be an authenticated user to make the request
        """
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_permission_required(self):
        """
        The authenticated user must have the correct permissions to make the request
        """
        user = get_user_model().objects.create_user("test")
        self.client.force_authenticate(user)
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class Covid19TriageViewSetTests(APITestCase, BaseEventTestCase):
    url = reverse("covid19triage-list")

    def test_data_validation(self):
        """
        The supplied data must be validated, and any errors returned
        """
        user = get_user_model().objects.create_user("test")
        user.user_permissions.add(Permission.objects.get(codename="add_covid19triage"))
        self.client.force_authenticate(user)
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_successful_request(self):
        """
        Should create a new Covid19Triage object in the database
        """
        user = get_user_model().objects.create_user("test")
        user.user_permissions.add(Permission.objects.get(codename="add_covid19triage"))
        self.client.force_authenticate(user)
        response = self.client.post(
            self.url,
            {
                "msisdn": "27820001001",
                "source": "USSD",
                "province": "ZA-WC",
                "city": "cape town",
                "age": Covid19Triage.AGE_18T40,
                "fever": False,
                "cough": False,
                "sore_throat": False,
                "exposure": Covid19Triage.EXPOSURE_NO,
                "tracing": True,
                "risk": Covid19Triage.RISK_LOW,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        [covid19triage] = Covid19Triage.objects.all()
        self.assertEqual(covid19triage.msisdn, "+27820001001")
        self.assertEqual(covid19triage.source, "USSD")
        self.assertEqual(covid19triage.province, "ZA-WC")
        self.assertEqual(covid19triage.city, "cape town")
        self.assertEqual(covid19triage.age, Covid19Triage.AGE_18T40)
        self.assertEqual(covid19triage.fever, False)
        self.assertEqual(covid19triage.cough, False)
        self.assertEqual(covid19triage.sore_throat, False)
        self.assertEqual(covid19triage.difficulty_breathing, None)
        self.assertEqual(covid19triage.exposure, Covid19Triage.EXPOSURE_NO)
        self.assertEqual(covid19triage.tracing, True)
        self.assertEqual(covid19triage.gender, "")
        self.assertEqual(covid19triage.location, "")
        self.assertEqual(covid19triage.muscle_pain, None)
        self.assertEqual(covid19triage.smell, None)
        self.assertEqual(covid19triage.preexisting_condition, "")
        self.assertIsInstance(covid19triage.deduplication_id, str)
        self.assertNotEqual(covid19triage.deduplication_id, "")
        self.assertEqual(covid19triage.risk, Covid19Triage.RISK_LOW)
        self.assertEqual(covid19triage.created_by, user.username)

    def test_duplicate_request(self):
        """
        Should create on the first request, and just return 200 on subsequent requests
        """
        user = get_user_model().objects.create_user("test")
        user.user_permissions.add(Permission.objects.get(codename="add_covid19triage"))
        self.client.force_authenticate(user)
        data = {
            "deduplication_id": "testid",
            "msisdn": "27820001001",
            "source": "USSD",
            "province": "ZA-WC",
            "city": "cape town",
            "age": Covid19Triage.AGE_18T40,
            "fever": False,
            "cough": False,
            "sore_throat": False,
            "exposure": Covid19Triage.EXPOSURE_NO,
            "tracing": True,
            "risk": Covid19Triage.RISK_LOW,
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_invalid_location_request(self):
        """
        Should create a new Covid19Triage object in the database
        """
        user = get_user_model().objects.create_user("test")
        user.user_permissions.add(Permission.objects.get(codename="add_covid19triage"))
        self.client.force_authenticate(user)
        response = self.client.post(
            self.url,
            {
                "msisdn": "+27820001001",
                "source": "USSD",
                "province": "ZA-WC",
                "city": "cape town",
                "age": Covid19Triage.AGE_18T40,
                "fever": False,
                "cough": False,
                "sore_throat": False,
                "exposure": Covid19Triage.EXPOSURE_NO,
                "tracing": True,
                "risk": Covid19Triage.RISK_LOW,
                "location": "invalid",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["location"], ["Invalid ISO6709 geographic coordinate"]
        )

    def test_get_list(self):
        """
        Should return the data, filtered by the querystring
        """
        user = get_user_model().objects.create_user("test")
        user.user_permissions.add(Permission.objects.get(codename="view_covid19triage"))
        self.client.force_authenticate(user)

        triage_old = Covid19Triage.objects.create(
            msisdn="+27820001001",
            source="USSD",
            province="ZA-WC",
            city="Cape Town",
            age=Covid19Triage.AGE_18T40,
            fever=False,
            cough=False,
            sore_throat=False,
            exposure=Covid19Triage.EXPOSURE_NO,
            tracing=True,
            risk=Covid19Triage.RISK_LOW,
        )

        # create triage_new but dont let the flake panic
        Covid19Triage.objects.create(
            msisdn="+27820001001",
            source="USSD",
            province="ZA-WC",
            city="Cape Town",
            age=Covid19Triage.AGE_18T40,
            fever=False,
            cough=False,
            sore_throat=False,
            exposure=Covid19Triage.EXPOSURE_NO,
            tracing=True,
            risk=Covid19Triage.RISK_LOW,
        )

        response = self.client.get(
            f"{self.url}?"
            f"{urlencode({'timestamp_gt': triage_old.timestamp.isoformat()})}"
        )

        r = dict(response.data[0])

        correct_data = {
            "msisdn": "+27820001001",
            "source": "USSD",
            "province": "ZA-WC",
            "city": "Cape Town",
            "age": Covid19Triage.AGE_18T40,
            "fever": False,
            "cough": False,
            "sore_throat": False,
            "difficulty_breathing": None,
            "exposure": Covid19Triage.EXPOSURE_NO,
            "tracing": True,
            "risk": Covid19Triage.RISK_LOW,
            "gender": "",
            "location": "",
            "muscle_pain": None,
            "smell": None,
            "preexisting_condition": "",
            "created_by": "",
            "data": {},
        }

        for k, v in r.items():
            if k in correct_data.keys():
                self.assertEqual(v, correct_data[k])

    def test_creates_user_profile(self):
        """
        The user profile should be created when the triage is saved
        """
        user = get_user_model().objects.create_user("test")
        user.user_permissions.add(Permission.objects.get(codename="add_covid19triage"))
        self.client.force_authenticate(user)
        self.client.post(
            self.url,
            {
                "msisdn": "27820001001",
                "source": "USSD",
                "province": "ZA-WC",
                "city": "cape town",
                "age": Covid19Triage.AGE_18T40,
                "fever": False,
                "cough": False,
                "sore_throat": False,
                "exposure": Covid19Triage.EXPOSURE_NO,
                "tracing": True,
                "risk": Covid19Triage.RISK_LOW,
            },
            format="json",
        )
        profile = HealthCheckUserProfile.objects.get(msisdn="+27820001001")
        self.assertEqual(profile.province, "ZA-WC")
        self.assertEqual(profile.city, "cape town")
        self.assertEqual(profile.age, Covid19Triage.AGE_18T40)


class Covid19TriageV2ViewSetTests(Covid19TriageViewSetTests):
    url = reverse("covid19triagev2-list")

    def test_get_list(self):
        """
        Should return the data, filtered by the querystring
        """
        user = get_user_model().objects.create_user("test")
        user.user_permissions.add(Permission.objects.get(codename="view_covid19triage"))
        self.client.force_authenticate(user)

        triage_old = Covid19Triage.objects.create(
            msisdn="+27820001001",
            source="USSD",
            province="ZA-WC",
            city="Cape Town",
            age=Covid19Triage.AGE_18T40,
            fever=False,
            cough=False,
            sore_throat=False,
            exposure=Covid19Triage.EXPOSURE_NO,
            tracing=True,
            risk=Covid19Triage.RISK_LOW,
        )

        # create triage_new but dont let the flake panic
        Covid19Triage.objects.create(
            msisdn="+27820001001",
            source="USSD",
            province="ZA-WC",
            city="Cape Town",
            age=Covid19Triage.AGE_18T40,
            fever=False,
            cough=False,
            sore_throat=False,
            exposure=Covid19Triage.EXPOSURE_NO,
            tracing=True,
            risk=Covid19Triage.RISK_LOW,
        )

        response = self.client.get(
            f"{self.url}?"
            f"{urlencode({'timestamp_gt': triage_old.timestamp.isoformat()})}"
        )

        r = dict(response.data[0])

        correct_data = {
            "msisdn": "+27820001001",
            "first_name": None,
            "last_name": None,
            "source": "USSD",
            "province": "ZA-WC",
            "city": "Cape Town",
            "age": Covid19Triage.AGE_18T40,
            "date_of_birth": None,
            "fever": False,
            "cough": False,
            "sore_throat": False,
            "difficulty_breathing": None,
            "exposure": Covid19Triage.EXPOSURE_NO,
            "confirmed_contact": None,
            "tracing": True,
            "risk": Covid19Triage.RISK_LOW,
            "gender": "",
            "location": "",
            "city_location": None,
            "muscle_pain": None,
            "smell": None,
            "preexisting_condition": "",
            "rooms_in_household": None,
            "persons_in_household": None,
            "created_by": "",
            "data": {},
        }
        for k, v in r.items():
            if k in correct_data.keys():
                self.assertEqual(v, correct_data[k])

    def test_returning_user(self):
        """
        Should create a new Covid19Triage object in the database using information
        from the first entry in the database
        """
        user = get_user_model().objects.create_user("test")
        user.user_permissions.add(Permission.objects.get(codename="add_covid19triage"))
        Covid19Triage.objects.create(
            msisdn="+27820001001",
            province="ZA-WC",
            city="cape town",
            fever=False,
            cough=False,
            sore_throat=False,
            tracing=True,
        )
        Covid19Triage.objects.create(
            msisdn="+27820001001",
            province="ZA-GT",
            city="sandton",
            fever=False,
            cough=False,
            sore_throat=False,
            tracing=True,
        )

        self.client.force_authenticate(user)
        response = self.client.post(
            self.url,
            {
                "msisdn": "27820001001",
                "source": "USSD",
                "age": Covid19Triage.AGE_18T40,
                "fever": False,
                "cough": False,
                "sore_throat": False,
                "exposure": Covid19Triage.EXPOSURE_NO,
                "tracing": True,
                "risk": Covid19Triage.RISK_LOW,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        triage_id = response.data["id"]
        covid19triage = Covid19Triage.objects.get(id=triage_id)
        self.assertEqual(covid19triage.province, "ZA-WC")
        self.assertEqual(covid19triage.city, "cape town")


class HealthCheckUserProfileViewSetTests(APITestCase, BaseEventTestCase):
    url = reverse("healthcheckuserprofile-detail", args=("+27820001001",))

    def test_no_data(self):
        """
        Should return a 404 if no data
        """
        user = get_user_model().objects.create_user("test")
        user.user_permissions.add(
            Permission.objects.get(codename="view_healthcheckuserprofile")
        )
        self.client.force_authenticate(user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_existing_healthchecks(self):
        """
        If there's no profile, but existing healthchecks, then it should construct the
        profile from those healthchecks
        """
        Covid19Triage.objects.create(
            msisdn="+27820001001",
            first_name="testname",
            fever=False,
            cough=False,
            sore_throat=False,
            tracing=True,
        )
        user = get_user_model().objects.create_user("test")
        user.user_permissions.add(
            Permission.objects.get(codename="view_healthcheckuserprofile")
        )
        self.client.force_authenticate(user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["msisdn"], "+27820001001")
        self.assertEqual(response.data["first_name"], "testname")

    def test_existing_profile(self):
        """
        It should return the existing profile
        """
        HealthCheckUserProfile.objects.create(
            msisdn="+27820001001", first_name="testname"
        )
        user = get_user_model().objects.create_user("test")
        user.user_permissions.add(
            Permission.objects.get(codename="view_healthcheckuserprofile")
        )
        self.client.force_authenticate(user)
        response = self.client.get(self.url)
        self.maxDiff = None
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["msisdn"], "+27820001001")
        self.assertEqual(response.data["first_name"], "testname")

    def test_update_profile(self):
        HealthCheckUserProfile.objects.create(
            msisdn="+27820001001", first_name="testname", data={"existing": "data"}
        )
        user = get_user_model().objects.create_user("test")
        user.user_permissions.add(
            Permission.objects.get(codename="change_healthcheckuserprofile")
        )
        self.client.force_authenticate(user)
        response = self.client.patch(self.url, {"first_name": "updated"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        [profile] = HealthCheckUserProfile.objects.all()
        self.assertEqual(profile.data, {"existing": "data"})
        self.assertEqual(profile.first_name, "updated")

    def test_update_profile_data(self):
        HealthCheckUserProfile.objects.create(
            msisdn="+27820001001",
            first_name="testname",
            last_name="test",
            data={"existing": "data"},
        )
        user = get_user_model().objects.create_user("test")
        user.user_permissions.add(
            Permission.objects.get(codename="change_healthcheckuserprofile")
        )
        self.client.force_authenticate(user)
        response = self.client.patch(
            self.url, {"data": {"something": "updated"}, "first_name": "updated"}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"]["something"], "updated")

        [profile] = HealthCheckUserProfile.objects.all()
        self.assertEqual(profile.data, {"existing": "data", "something": "updated"})
        self.assertEqual(profile.first_name, "updated")
        self.assertEqual(profile.last_name, "test")


class Covid19TriageV3ViewSetTests(Covid19TriageViewSetTests):
    url = reverse("covid19triagev3-list")

    def test_get_list(self):
        """
        Should return the data, filtered by the querystring
        """
        user = get_user_model().objects.create_user("test")
        user.user_permissions.add(Permission.objects.get(codename="view_covid19triage"))
        self.client.force_authenticate(user)

        triage_old = Covid19Triage.objects.create(
            msisdn="+27820001001",
            source="USSD",
            province="ZA-WC",
            city="Cape Town",
            age=Covid19Triage.AGE_18T40,
            fever=False,
            cough=False,
            sore_throat=False,
            exposure=Covid19Triage.EXPOSURE_NO,
            tracing=True,
            risk=Covid19Triage.RISK_LOW,
        )

        # create triage_new but dont let the flake panic
        Covid19Triage.objects.create(
            msisdn="+27820001001",
            source="USSD",
            province="ZA-WC",
            city="Cape Town",
            age=Covid19Triage.AGE_18T40,
            fever=False,
            cough=False,
            sore_throat=False,
            exposure=Covid19Triage.EXPOSURE_NO,
            tracing=True,
            risk=Covid19Triage.RISK_LOW,
            place_of_work=Covid19Triage.WORK_HEALTHCARE,
        )

        response = self.client.get(
            f"{self.url}?"
            f"{urlencode({'timestamp_gt': triage_old.timestamp.isoformat()})}"
        )

        r = dict(response.data[0])

        correct_data = {
            "msisdn": "+27820001001",
            "first_name": None,
            "last_name": None,
            "source": "USSD",
            "province": "ZA-WC",
            "city": "Cape Town",
            "age": Covid19Triage.AGE_18T40,
            "date_of_birth": None,
            "fever": False,
            "cough": False,
            "sore_throat": False,
            "difficulty_breathing": None,
            "exposure": Covid19Triage.EXPOSURE_NO,
            "confirmed_contact": None,
            "tracing": True,
            "risk": Covid19Triage.RISK_LOW,
            "gender": "",
            "location": "",
            "city_location": None,
            "muscle_pain": None,
            "smell": None,
            "preexisting_condition": "",
            "rooms_in_household": None,
            "persons_in_household": None,
            "created_by": "",
            "data": {},
            "place_of_work": Covid19Triage.WORK_HEALTHCARE,
        }
        for k, v in r.items():
            if k in correct_data.keys():
                self.assertEqual(v, correct_data[k])
