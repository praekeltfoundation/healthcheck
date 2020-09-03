from celery.decorators import periodic_task
from celery.task.schedules import crontab
from django.conf import settings
from temba_client.v2 import TembaClient

from tbconnect.models import TBCheck
from userprofile.models import HealthCheckUserProfile


@periodic_task(run_every=crontab(hour=1))
def perform_sync_to_rapidpro():
    if (
        settings.RAPIDPRO_URL
        and settings.RAPIDPRO_TOKEN
        and settings.RAPIDPRO_TBCONNECT_FLOW
    ):
        rapidpro = TembaClient(settings.RAPIDPRO_URL, settings.RAPIDPRO_TOKEN)

        # using data__contains to hit the GIN index - userprofile__data__gin_idx
        for contact in (
            HealthCheckUserProfile.objects.filter(
                data__contains={"follow_up_optin": True}
            )
            .exclude(data__contains={"synced_to_tb_rapidpro": True})
            .iterator()
        ):
            check = (
                TBCheck.objects.filter(msisdn=contact.msisdn)
                .order_by("-completed_timestamp")
                .first()
            )

            if check and check.should_sync_to_rapidpro:
                urn = f"tel:{contact.msisdn}"
                if check.source == "WhatsApp":
                    urn = f"whatsapp:{contact.msisdn.lstrip('+')}"

                rapidpro.create_flow_start(
                    urns=[urn],
                    flow=settings.RAPIDPRO_TBCONNECT_FLOW,
                    extra={
                        "risk": check.risk,
                        "source": check.source,
                        "completed_timestamp": check.completed_timestamp.strftime(
                            "%d/%m/%Y"
                        ),
                    },
                )

                contact.data["synced_to_tb_rapidpro"] = True
                contact.save()

    return "Finished syncing contacts to Rapidpro"
