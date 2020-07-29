import requests
from celery import Celery, shared_task, task  # noqa: F401, E261
from celery.decorators import periodic_task  # noqa: F401, E261
from celery.task.schedules import crontab  # noqa: F401, E261
from celery.utils.log import get_task_logger
from django.conf import settings
from django.utils import timezone

from contacts.models import Case

logger = get_task_logger(__name__)


@shared_task()
def send_contact_update(phone_number, confirmed_contact, case_id):
    connect_timeout, read_timeout = 5.0, 30.0

    headers = {
        "Authorization": f"Bearer {settings.TURN_API_KEY}",
        "Accept": "application/vnd.v1+json",
    }

    logger.info(f"https://whatsapp.turn.io/v1/contacts/{phone_number}/profile")

    response = requests.patch(
        url=f"https://whatsapp.turn.io/v1/contacts/{phone_number}/profile",
        json={"confirmed_contact": confirmed_contact},
        timeout=(connect_timeout, read_timeout),
        headers=headers,
    )

    if response.status_code == 201:
        # update case with respective dates
        case = Case.objects.get(id=case_id)
        case.is_active = False
        if confirmed_contact is True:
            case.date_notification_start = timezone.now()
            case.save(update_fields=["is_active", "date_notification_start"])
        else:
            case.date_notification_end = timezone.now()
            case.save(update_fields=["is_active", "date_notification_end"])

    # TODO: handle errors?

    return f"Finished sending contact {confirmed_contact} update for {phone_number}."


# TODO: write a similar task but with is_active where notification failed


@task
# @periodic_task(run_every=crontab(minute=50, hour=23))
def perform_nofitications_check():
    """
    Notify active cases about contact phase end
    """
    notification_pool = Case.objects.with_end_date().up_for_notification()

    logger.info(f"Pool of notifications: {notification_pool}")

    for case in notification_pool:
        send_contact_update.delay(
            phone_number=str(case.contact.msisdn),
            confirmed_contact=False,
            case_id=case.id,
        )

    return "Finished periodic notification check."
