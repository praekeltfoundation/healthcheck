from urllib.parse import urljoin

import requests
from celery.exceptions import SoftTimeLimitExceeded
from django.conf import settings
from requests.exceptions import RequestException

from healthcheck.celery import app


@app.task(
    autoretry_for=(RequestException, SoftTimeLimitExceeded),
    retry_backoff=True,
    max_retries=15,
    acks_late=True,
    soft_time_limit=10,
    time_limit=15,
)
def mark_turn_contact_healthcheck_complete(msisdn):
    if settings.API_URL is None or settings.TURN_API_KEY is None:
        return
    contact_id = msisdn.lstrip("+")
    url = urljoin(settings.API_URL, f"v1/contacts/{contact_id}/profile")
    response = requests.patch(
        url,
        json={"healthcheck_completed": True},
        headers={
            "Authorization": f"Bearer {settings.TURN_API_KEY}",
            "Accept": "application/vnd.v1+json",
        },
    )
    response.raise_for_status()
