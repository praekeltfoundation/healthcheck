from urllib.parse import urljoin

import requests
from celery import shared_task
from celery.exceptions import SoftTimeLimitExceeded
from celery.utils.log import get_task_logger
from django.conf import settings
from django.utils import timezone
from requests.exceptions import RequestException

from contacts.models import Case

logger = get_task_logger(__name__)


@shared_task(
    autoretry_for=(RequestException, SoftTimeLimitExceeded),
    max_retires=3,
    retry_backoff=True,
    soft_time_limit=15,
    time_limit=45,
    acks_late=True,
    # this will ensure turn.io rate limiter does not return 429
    rate_limit="60/m",
)
def send_contact_update(phone_number, confirmed_contact, case_id):
    # request should not take longer than 15 seconds total
    connect_timeout, read_timeout = 5.0, 10.0

    phone_number = phone_number.lstrip("+")

    response = requests.patch(
        url=urljoin(settings.API_DOMAIN, f"/v1/contacts/{phone_number}/profile"),
        json={"confirmed_contact": confirmed_contact},
        timeout=(connect_timeout, read_timeout),
        headers={
            "Authorization": f"Bearer {settings.TURN_API_KEY}",
            "Accept": "application/vnd.v1+json",
        },
    )

    response.raise_for_status()

    if response.status_code == 201:
        # update case with respective dates
        # we have to assume that the case exists
        case = Case.objects.get(id=case_id)
        if confirmed_contact is True:
            # case started
            case.date_notification_start = timezone.now()
            case.save(
                update_fields=["date_notification_start",]  # noqa: E231 E126 E261
            )
        else:
            # case ended
            case.is_active = False
            case.date_notification_end = timezone.now()
            case.save(update_fields=["is_active", "date_notification_end"])

    return f"Finished sending contact {confirmed_contact} update for {phone_number}."


@shared_task
def perform_notifications_check():
    """
    Notify active cases about contact phase end
    """
    if not settings.CONTACT_NOTIFICATION_ENABLED:
        return "Periodic notification check disabled."

    notification_pool = Case.objects.with_end_date().up_for_notification()

    logger.info(f"Pool of notifications: {notification_pool}")

    for case in notification_pool:
        send_contact_update.delay(
            phone_number=str(case.contact.msisdn),
            confirmed_contact=False,
            case_id=case.id,
        )

    return "Finished periodic notification check."
