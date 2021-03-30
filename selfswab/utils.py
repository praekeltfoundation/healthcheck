import re
import requests
from django.conf import settings
from urllib.parse import urljoin

from .models import SelfSwabRegistration


def get_next_unique_contact_id():
    all_options = set(["CV%04dH" % i for i in range(101, 10000)])
    existing_contact_ids = set(
        SelfSwabRegistration.objects.values("contact_id")
        .distinct()
        .values_list("contact_id", flat=True)
    )

    try:
        contact_id = sorted(list(all_options - existing_contact_ids))[0]
    except IndexError:
        contact_id = "-1"

    return contact_id


def is_barcode_format_valid(barcode):
    matches = re.findall(r"^(CP159600)|(00[0-9]|0[0-9][0-9]|[0-9][0-9][0-9])$", barcode)
    qa_matches = re.findall(r"^(CP999T99)|(00[0-9]|0[0-9][0-9]|100)$", barcode)
    return len(matches) == 2 or len(qa_matches) == 2


def upload_turn_media(media, content_type="application/pdf"):
    headers = {
        "Authorization": "Bearer {}".format(settings.SELFSWAB_TURN_TOKEN),
        "Content-Type": content_type,
    }

    response = requests.post(
        urljoin(settings.SELFSWAB_TURN_URL, f"v1/media"), headers=headers, data=media,
    )
    response.raise_for_status()
    return response.json()["media"][0]["id"]


def send_whatsapp_media_message(wa_id, media_type, media_id):
    headers = {
        "Authorization": "Bearer {}".format(settings.SELFSWAB_TURN_TOKEN),
        "Content-Type": "application/json",
    }

    data = {
        "recipient_type": "individual",
        "to": wa_id,
        "type": media_type,
        media_type: {"id": media_id},
    }

    response = requests.post(
        urljoin(settings.SELFSWAB_TURN_URL, "v1/messages"), headers=headers, json=data
    )
    response.raise_for_status()
    return response
