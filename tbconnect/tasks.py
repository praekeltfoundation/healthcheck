from celery.decorators import periodic_task
from celery.task.schedules import crontab
from django.conf import settings
from django_redis import get_redis_connection
from temba_client.v2 import TembaClient

from healthcheck import utils
from tbconnect.models import TBCheck, TBTest
from userprofile.models import HealthCheckUserProfile


@periodic_task(run_every=crontab(minute="*/5"))
def perform_sync_to_rapidpro():
    r = get_redis_connection()
    if r.get("perform_sync_to_rapidpro"):
        return

    with r.lock("perform_sync_to_rapidpro", 1800):
        if (
            settings.RAPIDPRO_URL
            and settings.RAPIDPRO_TOKEN
            and settings.RAPIDPRO_TBCONNECT_FLOW
        ):
            rapidpro = TembaClient(settings.RAPIDPRO_URL, settings.RAPIDPRO_TOKEN)

            # using data__contains to hit the GIN index - userprofile__data__gin_idx
            for contact in HealthCheckUserProfile.objects.filter(
                data__contains={"synced_to_tb_rapidpro": False}
            ).iterator():
                check = (
                    TBCheck.objects.filter(msisdn=contact.msisdn)
                    .order_by("-completed_timestamp")
                    .first()
                )

                if check:
                    urn = f"tel:{contact.msisdn}"
                    if check.source == "WhatsApp":
                        urn = f"whatsapp:{contact.msisdn.lstrip('+')}"

                    rapidpro.create_flow_start(
                        urns=[urn],
                        flow=settings.RAPIDPRO_TBCONNECT_FLOW,
                        extra={
                            "risk": check.risk,
                            "source": check.source,
                            "follow_up_optin": contact.data.get(
                                "follow_up_optin", check.follow_up_optin
                            ),
                            "completed_timestamp": check.completed_timestamp.strftime(
                                "%d/%m/%Y"
                            ),
                            "exposure": check.exposure,
                        },
                    )

                    contact.data["synced_to_tb_rapidpro"] = True
                    contact.save()

    return "Finished syncing contacts to Rapidpro"


@periodic_task(run_every=crontab(minute="*/5"))
def perform_etl():
    r = get_redis_connection()
    if r.get("perform_etl_tb_connect"):
        return

    models = {
        "checks": {
            "model": TBCheck,
            "field": "timestamp",
            "fields": {
                "deduplication_id": "STRING",
                "msisdn": "STRING",
                "timestamp": "TIMESTAMP",
                "source": "STRING",
                "province": "STRING",
                "age": "STRING",
                "gender": "STRING",
                "location_latitude": "FLOAT",
                "location_longitude": "FLOAT",
                "city_latitude": "FLOAT",
                "city_longitude": "FLOAT",
                "cough": "BOOLEAN",
                "fever": "BOOLEAN",
                "sweat": "BOOLEAN",
                "weight": "BOOLEAN",
                "exposure": "STRING",
                "risk": "STRING",
                "follow_up_optin": "BOOLEAN",
                "language": "STRING",
            },
        },
        "tests": {
            "model": TBTest,
            "field": "updated_at",
            "fields": {
                "deduplication_id": "STRING",
                "msisdn": "STRING",
                "source": "STRING",
                "result": "STRING",
                "timestamp": "TIMESTAMP",
                "updated_at": "TIMESTAMP",
            },
        },
    }

    with r.lock("perform_etl_tb_connect", 1800):
        utils.sync_models_to_bigquery(
            settings.TBCONNECT_BQ_KEY_PATH, settings.TBCONNECT_BQ_DATASET, models
        )
