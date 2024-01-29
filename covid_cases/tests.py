import gzip
import json
from datetime import date

import responses
from django.core.cache import cache
from django.core.files import File
from django.test import override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from covid_cases.clients import NICDGISClient
from covid_cases.models import (
    District,
    Province,
    SACoronavirusCaseImage,
    SACoronavirusCounter,
    SubDistrict,
    Ward,
    WardCase,
)
from covid_cases.tasks import (
    scrape_nicd_gis,
    scrape_sacoronavirus_case_images,
    scrape_sacoronavirus_homepage,
)
from covid_cases.utils import normalise_text


def generate_mock_db_data(self):
    Province.get_province.cache_clear()
    District.get_district.cache_clear()
    SubDistrict.get_sub_district.cache_clear()
    cache.delete("latest_image")

    self.province = Province.objects.create(name="Western Cape")
    self.district = District.objects.create(name="West Coast", province=self.province)
    self.sub_district = SubDistrict.objects.create(
        name="Matzikama", subdistrict_id=260, district=self.district
    )
    self.ward = Ward.objects.create(
        ward_id="10101001", ward_number="1", sub_district=self.sub_district
    )
    self.ward_case = WardCase.objects.create(
        object_id=1,
        ward=self.ward,
        male=401,
        female=364,
        age_1_10=12,
        age_11_20=88,
        age_21_30=153,
        age_31_40=148,
        age_41_50=186,
        age_51_60=110,
        age_61_70=46,
        age_71_80=13,
        age_81=9,
        unknown_age=0,
        unknown_gender=0,
        latest=20,
        total_number_of_cases=765,
        date=date(2021, 12, 9),
    )

    with open("covid_cases/mock_data/20211209-dec-map.jpg", "rb") as f:
        self.image = SACoronavirusCaseImage.objects.create(
            image=File(f), date=date(2021, 12, 9)
        )

    self.counter = SACoronavirusCounter.objects.create(
        tests=20238805,
        positive=3167497,
        recoveries=2913232,
        deaths=90137,
        vaccines=27090975,
        date=date(2021, 12, 9),
    )


class CovidCasesViewsTests(APITestCase):
    setUp = generate_mock_db_data

    def test_get_ward_cases_flat(self):
        url = reverse("wardcase-flat")
        with self.assertNumQueries(1):
            response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        [ward_case] = response.data["results"]
        self.assertEqual(ward_case["ward_id"], "10101001")
        self.assertEqual(ward_case["ward_number"], "1")
        self.assertEqual(ward_case["subdistrict"], "Matzikama")
        self.assertEqual(ward_case["subdistrict_id"], 260)
        self.assertEqual(ward_case["district"], "West Coast")
        self.assertEqual(ward_case["province"], "Western Cape")
        self.assertEqual(ward_case["male"], 401)
        self.assertEqual(ward_case["female"], 364)
        self.assertEqual(ward_case["unknown_gender"], 0)
        self.assertEqual(ward_case["age_1_10"], 12)
        self.assertEqual(ward_case["age_11_20"], 88)
        self.assertEqual(ward_case["age_21_30"], 153)
        self.assertEqual(ward_case["age_31_40"], 148)
        self.assertEqual(ward_case["age_41_50"], 186)
        self.assertEqual(ward_case["age_51_60"], 110)
        self.assertEqual(ward_case["age_61_70"], 46)
        self.assertEqual(ward_case["age_71_80"], 13)
        self.assertEqual(ward_case["age_81"], 9)
        self.assertEqual(ward_case["unknown_age"], 0)
        self.assertEqual(ward_case["latest"], 20)
        self.assertEqual(ward_case["total_number_of_cases"], 765)


class CovidCasesTasksTests(APITestCase):
    setUp = generate_mock_db_data

    def test_normalise_text(self):
        self.assertEqual(normalise_text("  test TEXT "), "Test Text")

    @responses.activate
    def test_get_api_total_cases(self):
        with gzip.open("covid_cases/mock_data/gis_nicd.txt.gz") as f:
            responses.add(
                method="GET",
                url="https://gis.nicd.ac.za/hosting/rest/services/WARDS_MN/MapServer/0/query",
                body=f.read(),
            )
        client = NICDGISClient()
        with gzip.open("covid_cases/mock_data/gis_nicd.txt.gz") as f:
            self.assertEqual(client.get_total_cases(), 3051206)

    def test_get_database_total_cases(self):
        WardCase.objects.create(
            object_id=2,
            ward=self.ward,
            male=63,
            female=61,
            age_1_10=1,
            age_11_20=13,
            age_21_30=27,
            age_31_40=24,
            age_41_50=22,
            age_51_60=23,
            age_61_70=7,
            age_71_80=7,
            age_81=1,
            unknown_age=0,
            unknown_gender=1,
            latest=0,
            total_number_of_cases=125,
            date=date(2021, 12, 8),
        )
        self.assertEqual(WardCase.objects.get_total_cases(), 765)

    def test_get_ward(self):
        self.assertEqual(
            self.ward,
            Ward.get_ward(
                province="Western Cape",
                district="West Coast",
                sub_district="Matzikama",
                sub_district_id=260,
                ward_id="10101001",
                ward_number="1",
            ),
        )
        with self.assertNumQueries(1):
            Ward.get_ward(
                province="Western Cape",
                district="West Coast",
                sub_district="Matzikama",
                sub_district_id=260,
                ward_id="10101001",
                ward_number="1",
            ),

    @responses.activate
    @override_settings(ENABLE_NICD_GIS_SCRAPING=True)
    def test_scrape_nicd_gis(self):
        WardCase.objects.all().delete()
        with gzip.open("covid_cases/mock_data/gis_nicd.txt.gz") as f:
            data = json.loads(f.read())
            # Only do the first 100 so that the test remains quick
            data["features"] = data["features"][:100]
            responses.add(
                method="GET",
                url="https://gis.nicd.ac.za/hosting/rest/services/WARDS_MN/MapServer/0/query",
                body=json.dumps(data),
            )
        scrape_nicd_gis()
        self.assertEqual(WardCase.objects.count(), 100)


class ScrapeSACoronavirusHomepageTests(APITestCase):
    @responses.activate
    @override_settings(ENABLE_SACORONAVIRUS_SCRAPING=True)
    def test_scrape_sacoronavirus_hompage(self):
        with gzip.open("covid_cases/mock_data/sacoronavirus.txt.gz") as f:
            responses.add(
                method="GET",
                url="https://sacoronavirus.co.za",
                body=f.read(),
            )
        result = scrape_sacoronavirus_homepage()
        self.assertIn("tests=19988045", result)
        self.assertEqual(SACoronavirusCounter.objects.all().count(), 1)

        result = scrape_sacoronavirus_homepage()
        self.assertIn("Skipping, no increase", result)


class ScrapeSACoronavirusImageTests(APITestCase):
    @responses.activate
    @override_settings(ENABLE_SACORONAVIRUS_SCRAPING=True)
    def test_scape_sacoronavirus_image(self):
        with gzip.open("covid_cases/mock_data/sacoronavirus_image.html.gz") as f:
            responses.add(
                method="GET",
                url="https://sacoronavirus.co.za/category/daily-cases",
                body=f.read(),
            )
        with open("covid_cases/mock_data/20211209-dec-map.jpg", "rb") as f:
            responses.add(
                method="GET",
                url="https://sacoronavirus.b-cdn.net/wp-content/uploads/2021/12/09-dec-map.jpg",
                body=f.read(),
            )
        result = scrape_sacoronavirus_case_images()
        self.assertEqual(result, "Downloaded 1 images")
        self.assertEqual(SACoronavirusCaseImage.objects.all().count(), 1)


class ContactNDoHCasesTests(APITestCase):
    setUp = generate_mock_db_data

    def test_missing_previous_day(self):
        url = reverse("contactndoh-list")
        response = self.client.get(url)
        self.assertEqual(response.data["image"]["id"], self.image.id)
        self.assertEqual(response.data["counter"]["id"], self.counter.id)
        self.assertNotIn("daily", response.data)

    def test_previous_day_present(self):
        SACoronavirusCounter.objects.create(
            tests=20238795,
            positive=3167467,
            recoveries=2913182,
            deaths=90067,
            vaccines=27090885,
            date=date(2021, 12, 8),
        )
        url = reverse("contactndoh-list")
        response = self.client.get(url)
        self.assertEqual(response.data["image"]["id"], self.image.id)
        self.assertEqual(response.data["counter"]["id"], self.counter.id)
        self.assertEqual(
            response.data["daily"],
            {
                "tests": 10,
                "positive": 30,
                "recoveries": 50,
                "deaths": 70,
                "vaccines": 90,
            },
        )
