from celery.decorators import periodic_task
from celery.task.schedules import crontab
from django.conf import settings
from django_redis import get_redis_connection
from temba_client.v2 import TembaClient

from healthcheck import utils
from lnconnect.models import LNCheck
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
            and settings.RAPIDPRO_LIFENET_FLOW
        ):
            rapidpro = TembaClient(settings.RAPIDPRO_URL, settings.RAPIDPRO_TOKEN)

            # using data__contains to hit the GIN index - userprofile__data__gin_idx
            for contact in HealthCheckUserProfile.objects.filter(
                data__contains={"synced_to_tb_rapidpro": False}
            ).iterator():
                check = (
                    LNCheck.objects.filter(msisdn=contact.msisdn)
                    .order_by("-completed_timestamp")
                    .first()
                )

                if check:
                    urn = f"tel:{contact.msisdn}"
                    if check.source == "WhatsApp":
                        urn = f"whatsapp:{contact.msisdn.lstrip('+')}"

                    rapidpro.create_flow_start(
                        urns=[urn],
                        flow=settings.RAPIDPRO_LIFENET_FLOW,
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

                    contact.data["synced_to_lifenet_rapidpro"] = True
                    contact.save()

    return "Finished syncing contacts to Rapidpro"


@periodic_task(run_every=crontab(minute="*/5"))
def perform_etl():
    r = get_redis_connection()
    if r.get("perform_etl_tb_connect"):
        return

    models = {
        "checks": {
            "model": LNCheck,
            "field": "timestamp",
            "fields": {
                "deduplication_id": "STRING",
                "msisdn": "STRING",
                "timestamp": "TIMESTAMP",
                "source": "STRING",
                "age": "STRING",
                "cough": "BOOLEAN",
                "fever": "BOOLEAN",
                "sore_throat": "BOOLEAN",
                "difficulty_breathing": "BOOLEAN",
                "muscle_pain": "BOOLEAN",
                "smell": "BOOLEAN",
                "exposure": "STRING",
                "risk": "STRING",
                "tracing": "BOOLEAN",
                "language": "STRING",
            },
        }
    }

    with r.lock("perform_etl_lifenet", 1800):
        utils.sync_models_to_bigquery(
            settings.LIFENET_BQ_KEY_PATH, settings.LIFENET_BQ_DATASET, models
        )
