from celery.decorators import periodic_task
from celery.task.schedules import crontab
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

from django_redis import get_redis_connection
from temba_client.v2 import TembaClient
import requests
from selfswab.models import SelfSwabScreen, SelfSwabTest
from healthcheck import utils


@periodic_task(run_every=crontab(minute="*/5"))
def poll_meditech_api_for_results():
    r = get_redis_connection()
    if r.get("poll_meditech_api_for_results"):
        return
    with r.lock("poll_meditech_api_for_results", 1800):
        if (
            settings.MEDITECH_URL
            and settings.RAPIDPRO_URL
            and settings.SELFSWAB_RAPIDPRO_TOKEN
            and settings.SELFSWAB_RAPIDPRO_FLOW
        ):
            rapidpro = TembaClient(
                settings.RAPIDPRO_URL, settings.SELFSWAB_RAPIDPRO_TOKEN
            )

            barcodes = list(
                SelfSwabTest.objects.filter(
                    result=SelfSwabTest.RESULT_PENDING
                ).values_list("barcode", flat=True)
            )
            response = requests.post(
                url=settings.MEDITECH_URL,
                headers={"Content-Type": "application/json"},
                json={"barcodes": barcodes},
            )
            response.raise_for_status()
            results = response.json()["barcodes"]
            for barcode, result in results.items():
                if result != SelfSwabTest.RESULT_PENDING:
                    try:
                        registration = SelfSwabTest.objects.get(barcode=barcode)
                    except (ObjectDoesNotExist):
                        continue

                    if result == "":
                        result = SelfSwabTest.RESULT_PENDING
                    registration.result = result
                    rapidpro.create_flow_start(
                        urns=f"whatsapp:{registration.msisdn}",
                        flow=settings.SELFSWAB_RAPIDPRO_FLOW,
                        extra={
                            "result": registration.result,
                            "updated_at": registration.updated_at.strftime("%d/%m/%Y"),
                        },
                    )
                    registration.save()

    return "Finished syncing test results to Rapidpro"


@periodic_task(run_every=crontab(minute="*/5"))
def perform_etl():
    r = get_redis_connection()
    if r.get("perform_etl_selfswab"):
        return

    models = {
        "screens": {
            "model": SelfSwabScreen,
            "field": "timestamp",
            "fields": {
                "id": "STRING",
                "contact_id": "STRING",
                "msisdn": "STRING",
                "age": "STRING",
                "gender": "STRING",
                "facility": "STRING",
                "risk_type": "STRING",
                "timestamp": "TIMESTAMP",
                "occupation": "STRING",
                "employee_number": "STRING",
                "pre_existing_condition": "STRING",
                "cough": "BOOLEAN",
                "fever": "BOOLEAN",
                "shortness_of_breath": "BOOLEAN",
                "body_aches": "BOOLEAN",
                "loss_of_taste_smell": "BOOLEAN",
                "sore_throat": "BOOLEAN",
                "additional_symptoms": "BOOLEAN",
            },
        },
        "tests": {
            "model": SelfSwabTest,
            "field": "updated_at",
            "fields": {
                "id": "STRING",
                "contact_id": "STRING",
                "msisdn": "STRING",
                "result": "STRING",
                "barcode": "STRING",
                "timestamp": "TIMESTAMP",
                "updated_at": "TIMESTAMP",
            },
        },
    }

    with r.lock("perform_etl_selfswab", 1800):
        utils.sync_models_to_bigquery(
            settings.SELFSWAB_BQ_KEY_PATH, settings.SELFSWAB_BQ_DATASET, models
        )
