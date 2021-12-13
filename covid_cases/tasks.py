from datetime import date

import requests
from celery.exceptions import SoftTimeLimitExceeded
from django.conf import settings
from django.core.files.base import ContentFile
from django.db import transaction
from requests.exceptions import RequestException

from covid_cases.clients import NICDGISClient, SACoronavirusClient
from covid_cases.models import (
    SACoronavirusCaseImage,
    SACoronavirusCounter,
    Ward,
    WardCase,
    WardCaseQuerySet,
)
from covid_cases.utils import get_filename_from_url, normalise_text
from healthcheck.celery import app


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
    client = NICDGISClient()

    # Only update if the total number of cases has increased
    db_total = WardCase.objects.get_total_cases()
    api_total = client.get_total_cases()
    if db_total >= api_total:
        return f"Skipping, database cases {db_total} >= API cases {api_total}"

    created, updated = 0, 0
    with transaction.atomic():
        for record in client.get_ward_cases_data()["features"]:
            record = record["attributes"]
            ward = Ward.get_ward(
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


@app.task(
    autoretry_for=(RequestException, SoftTimeLimitExceeded),
    max_retries=5,
    retry_backoff=True,
    soft_time_limit=60,
    time_limit=90,
    acks_late=True,
)
def scrape_sacoronavirus_homepage():
    if not settings.ENABLE_SACORONAVIRUS_SCRAPING:
        return "Skipping task, disabled in config"
    client = SACoronavirusClient()
    # Only update if any of the numbers have increased
    try:
        api_values = client.get_homepage_counters()
        db_values = SACoronavirusCounter.objects.latest("date")
        if all(
            (
                db_values.tests >= api_values.tests,
                db_values.positive >= api_values.positive,
                db_values.recoveries >= api_values.recoveries,
                db_values.deaths >= api_values.deaths,
                db_values.vaccines >= api_values.vaccines,
            )
        ):
            return f"Skipping, no increases in values {api_values}"
    except SACoronavirusCounter.DoesNotExist:
        pass

    _, c = SACoronavirusCounter.objects.update_or_create(
        date=date.today(),
        defaults={
            "tests": api_values.tests,
            "positive": api_values.positive,
            "recoveries": api_values.recoveries,
            "deaths": api_values.deaths,
            "vaccines": api_values.vaccines,
        },
    )
    if c:
        return f"Created {date.today().isoformat()} {api_values}"
    else:
        return f"Updated {date.today().isoformat()} {api_values}"


@app.task(
    autoretry_for=(RequestException, SoftTimeLimitExceeded),
    max_retries=5,
    retry_backoff=True,
    soft_time_limit=300,
    time_limit=400,
    acks_late=True,
)
def scrape_sacoronavirus_case_images():
    if not settings.ENABLE_SACORONAVIRUS_SCRAPING:
        return "Skipping task, disabled in config"
    client = SACoronavirusClient()
    # Only update if we don't have this file yet
    total = 0
    for image in client.get_daily_cases_image_urls():
        try:
            SACoronavirusCaseImage.objects.get(url=image.url)
            continue
        except SACoronavirusCaseImage.DoesNotExist:
            pass
        image_data = requests.get(
            image.url, headers={"User-Agent": "contactndoh-whatsapp"}, timeout=30
        )
        image_data.raise_for_status()
        file = ContentFile(
            image_data.content, name=get_filename_from_url(image_data.url)
        )
        SACoronavirusCaseImage.objects.create(
            url=image.url, image=file, date=image.date
        )
        total += 1
    return f"Downloaded {total} images"
