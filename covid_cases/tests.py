from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from covid_cases.models import Province, District, SubDistrict, Ward, WardCase
from covid_cases.views import WardCaseViewSet


class CovidCasesViewsTests(APITestCase):
    def setUp(self):
        self.province = Province.objects.create(name="Western Cape")
        self.district = District.objects.create(
            name="West Coast", province=self.province
        )
        self.sub_district = SubDistrict.objects.create(
            name="Matzikama", subdistrict_id=260, district=self.district
        )
        self.ward = Ward.objects.create(
            ward_id="10101001", ward_number="1", sub_district=self.sub_district
        )
        self.ward_case = WardCase.objects.create(
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
            latest=0,
            total_number_of_cases=765,
        )

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
        self.assertEqual(ward_case["latest"], 0)
        self.assertEqual(ward_case["total_number_of_cases"], 765)
