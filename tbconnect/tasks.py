from functools import wraps

from celery.decorators import periodic_task
from celery.task.schedules import crontab
from django.conf import settings
from django_redis import get_redis_connection
from temba_client.v2 import TembaClient

from tbconnect.models import TBCheck
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
