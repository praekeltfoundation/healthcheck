from celery import shared_task
from celery.exceptions import SoftTimeLimitExceeded
from celery.utils.log import get_task_logger
from django.conf import settings
from requests.exceptions import RequestException
from temba_client.exceptions import TembaException
from temba_client.v2 import TembaClient

from real411.models import Complaint

logger = get_task_logger(__name__)

rapidpro_client = TembaClient(settings.RAPIDPRO_URL, settings.RAPIDPRO_TOKEN)


@shared_task(
    autoretry_for=(RequestException, TembaException, SoftTimeLimitExceeded),
    max_retries=20,
    retry_backoff=True,
    soft_time_limit=15,
    time_limit=20,
    acks_late=True,
)
def process_complaint_update(update: dict) -> dict:
    """
    Processes a complaint update, sending an update message to the user. `update` must
    be validated by the `ComplaintUpdateSerializer`, and `update.complaint_ref` must
    have a corresponding `Complaint` object in the database.
    """
    logger.info(f"Processing complaint update with data {update}")

    complaint = Complaint.objects.get(complaint_ref=update["complaint_ref"])
    result = rapidpro_client.create_flow_start(
        settings.RAPIDPRO_REAL411_FLOW,
        urns=[f"whatsapp:{complaint.msisdn.lstrip('+')}"],
        restart_participants=True,
        extra=update,
    )
    return result.serialize()
