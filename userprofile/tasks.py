from urllib.parse import urljoin

import requests
from celery import shared_task
from celery.exceptions import SoftTimeLimitExceeded
from django.conf import settings
from requests.exceptions import RequestException


@shared_task(
    autoretry_for=(RequestException, SoftTimeLimitExceeded),
    max_retires=3,
    retry_backoff=True,
    soft_time_limit=15,
    time_limit=45,
    acks_late=True,
)
def update_turn_contact(msisdn, field, value):
    # request should not take longer than 15 seconds total
    connect_timeout, read_timeout = 5.0, 10.0

    msisdn = msisdn.lstrip("+")

    response = requests.patch(
        url=urljoin(settings.API_DOMAIN, f"/v1/contacts/{msisdn}/profile"),
        json={field: value},
        timeout=(connect_timeout, read_timeout),
        headers={
            "Authorization": f"Bearer {settings.TURN_API_KEY}",
            "Accept": "application/vnd.v1+json",
        },
    )

    response.raise_for_status()

    return f"Finished updating contact {field}={value}."
