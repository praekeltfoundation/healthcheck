from celery import shared_task
from django.conf import settings
from django_redis import get_redis_connection
from temba_client.v2 import TembaClient

from healthcheck import utils
from tbconnect.models import TBCheck, TBTest
from userprofile.models import HealthCheckUserProfile
import requests


@shared_task
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

                force_ussd_followup = False

                if check:
                    # Force prefered channel for shared device activations.
                    if check.activation and check.activation.endswith("_agent"):
                        force_ussd_followup = True

                    urn = f"tel:{contact.msisdn}"
                    if check.source == "WhatsApp" and not force_ussd_followup:
                        urn = f"whatsapp:{contact.msisdn.lstrip('+')}"

                    tbconnect_group_arm_timestamp = None
                    if contact.tbconnect_group_arm_timestamp:
                        tbconnect_group_arm_timestamp = (
                            contact.tbconnect_group_arm_timestamp.strftime(
                                "%Y-%m-%dT%H:%M:%SZ"
                            )
                        )
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
                            "language": contact.language,
                            "activation": check.activation,
                            "tbconnect_group_arm": contact.tbconnect_group_arm,
                            "tbconnect_group_arm_timestamp": tbconnect_group_arm_timestamp,
                            "commit_get_tested": check.commit_get_tested,
                            "research_consent": check.research_consent,
                        },
                    )

                    contact.data["synced_to_tb_rapidpro"] = True
                    contact.save()

    return "Finished syncing contacts to Rapidpro"


@shared_task
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
                "activation": "STRING",
                "originating_msisdn": "STRING",
                "commit_get_tested": "STRING",
                "research_consent": "BOOLEAN",
                "clinic_to_visit": "STRING",
                "clinic_visit_day": "STRING",
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


@shared_task
def send_tbcheck_data_to_cci(data):
    msisdn = data.get("CLI")

    profile = get_user_profile(msisdn)

    if profile:
        # update or append data with profile and gender
        data.update({"Province": profile.province, "Gender": profile.gender})

        # Send user data to cci
        headers = {
            "Content-Type": "application/json",
        }
        response = requests.post(url=settings.CCI_URL, headers=headers, json=data)

        if (
            response.status_code == 200
            and b'"Received Successfully"' == response.content
        ):
            return "CCI data submitted successfully"
        response.raise_for_status()
        raise Exception(
            "CCI data Submission failed {} , Data sent: {} , Data Type: {}".format(
                response.content, data, type(data)
            )
        )
    raise Exception("User profile {} not found".format(msisdn))


def get_user_profile(msisdn=None):
    try:
        profile = HealthCheckUserProfile.objects.get(msisdn=msisdn)
        if profile:
            return profile
    except HealthCheckUserProfile.DoesNotExist:
        return None
