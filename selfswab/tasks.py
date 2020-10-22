from celery.decorators import periodic_task
from celery.task.schedules import crontab
from django.conf import settings

from django_redis import get_redis_connection
from temba_client.v2 import TembaClient
import requests
from selfswab.models import SelfSwabTest


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

    barcodes = SelfSwabTest.objects.filter(
        result=SelfSwabTest.RESULT_PENDING
    ).values_list("barcode", flat=True)
    response = requests.post(settings.MEDITECH_URL, data={"barcodes": barcodes})
    response.raise_for_status()
    results = response.json()["barcodes"]
    for barcode, result in results.items():
        if result != "pending":
            try:
                registration = SelfSwabTest.objects.get(barcode=barcode)
            except (ValueError):
                return

            registration.result = result
            registration.save()
            rapidpro.create_flow_start(
                urns=f"whatsapp:{registration.msisdn}",
                flow=settings.SELFSWAB_RAPIDPRO_FLOW,
                extra={
                    "result": registration.result,
                    "updated_at": registration.updated_at.strftime("%d/%m/%Y"),
                },
            )

    return "Finished syncing test results to Rapidpro"
