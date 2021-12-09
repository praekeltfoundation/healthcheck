import re
from datetime import date
from functools import lru_cache

import requests
from celery.exceptions import SoftTimeLimitExceeded
from django.conf import settings
from django.db import transaction
from django.db.models import Max, Sum
from requests.exceptions import RequestException

from covid_cases.models import District, Province, SubDistrict, Ward, WardCase
from healthcheck.celery import app


def normalise_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().title()


def get_api_total_cases(api_data: dict) -> int:
    total_cases = 0
    for record in api_data["features"]:
        total_cases += record["attributes"]["Tot_No_of_Cases"]
    return total_cases


def get_database_total_cases() -> int:
    latest_date = WardCase.objects.aggregate(latest_date=Max("date"))["latest_date"]
    return (
        WardCase.objects.filter(date=latest_date).aggregate(
            total=Sum("total_number_of_cases")
        )["total"]
        or 0
    )


@lru_cache(maxsize=None)
def get_province(province: str):
    province, _ = Province.objects.get_or_create(name=province)
    return province


@lru_cache(maxsize=None)
def get_district(province: str, district: str):
    province = get_province(province)
    district, _ = District.objects.get_or_create(province=province, name=district)
    return district


@lru_cache(maxsize=None)
def get_sub_district(
    province: str, district: str, sub_district: str, sub_district_id: int
):
    district = get_district(province, district)
    sub_district, _ = SubDistrict.objects.get_or_create(
        district=district, name=sub_district, subdistrict_id=sub_district_id
    )
    return sub_district


def get_ward(
    province: str,
    district: str,
    sub_district: str,
    sub_district_id: int,
    ward_id: str,
    ward_number: str,
) -> Ward:
    sub_district = get_sub_district(province, district, sub_district, sub_district_id)
    ward, _ = Ward.objects.get_or_create(
        sub_district=sub_district, ward_id=ward_id, ward_number=ward_number
    )
    return ward


@app.task(
    autoretry_for=(RequestException, SoftTimeLimitExceeded),
    max_retries=5,
    retry_backoff=True,
    soft_time_limit=60,
    time_limit=90,
    acks_late=True,
)
def scrape_nicd_gis():
    if not settings.ENABLE_NICD_GIS_SCRAPING:
        return "Skipping task, disabled in config"
    response = requests.get(
        url="https://gis.nicd.ac.za/hosting/rest/services/WARDS_MN/MapServer/0/query",
        params={
            "where": "1=1",
            "outFields": "*",
            "returnGeometry": "false",
            "f": "json",
        },
        headers={"User-Agent": "contactndoh-whatsapp"},
        timeout=50,
    )
    response.raise_for_status()

    # Only update if the total number of cases has increased
    db_total = get_database_total_cases()
    api_total = get_api_total_cases(response.json())
    if db_total >= api_total:
        return f"Skipping, database cases {db_total} >= API cases {api_total}"

    created, updated = 0, 0
    with transaction.atomic():
        for record in response.json()["features"]:
            record = record["attributes"]
            ward = get_ward(
                province=normalise_text(record["Province"] or ""),
                district=normalise_text(record["District"] or ""),
                sub_district=normalise_text(record["Sub_Distri"] or ""),
                sub_district_id=record["Sub_district_ID"],
                ward_id=normalise_text(record["WardID"] or ""),
                ward_number=normalise_text(record["WardNumber"] or ""),
            )

            _, c = WardCase.objects.update_or_create(
                object_id=record["OBJECTID_1"],
                date=date.today(),
                defaults={
                    "ward": ward,
                    "male": record["Male"],
                    "female": record["Female"],
                    "unknown_gender": record["Unknown_Ge"],
                    "age_1_10": record["Age_1_10_y"],
                    "age_11_20": record["Age_11_20_"],
                    "age_21_30": record["Age_21_30_"],
                    "age_31_40": record["Age_31_40_"],
                    "age_41_50": record["Age_41_50_"],
                    "age_51_60": record["Age_51_60_"],
                    "age_61_70": record["Age_61_70_"],
                    "age_71_80": record["Age_71_80_"],
                    "age_81": record["Age_81_yrs"],
                    "unknown_age": record["Unknown_Ag"],
                    "latest": record["Latest"],
                    "total_number_of_cases": record["Tot_No_of_Cases"],
                },
            )
            if c:
                created += 1
            else:
                updated += 1
    return f"Created {created} case entries, updated {updated} case entries"
