import cv2
import zbar
import re
import requests
import tempfile
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
        "Authorization": f"Bearer {settings.SELFSWAB_TURN_TOKEN}",
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


def get_barcode_from_last_inbound_image(wa_id):
    response = get_whatsapp_messages(wa_id)
    media = None
    for message in response["messages"]:
        if (
            message["type"] == "image"
            and message["_vnd"]["v1"]["direction"] == "inbound"
        ):
            media = get_whatsapp_media(message["image"]["id"])
            break

    if media:
        with tempfile.NamedTemporaryFile(mode="wb") as temp_image:
            temp_image.write(media)
            image = cv2.imread(temp_image.name, cv2.IMREAD_GRAYSCALE)
            _, bw_image = cv2.threshold(image, 127, 255, cv2.THRESH_BINARY)

            scanner = zbar.Scanner()
            results = scanner.scan(bw_image)

            if len(results) == 1:
                return results[0].data.decode("utf-8"), None
            elif len(results) > 1:
                return None, "Multiple barcodes in image"

    return None, "No barcodes found"


def get_whatsapp_messages(wa_id):
    headers = {
        "Authorization": f"Bearer {settings.SELFSWAB_TURN_TOKEN}",
        "content-type": "application/json",
        "Accept": "application/vnd.v1+json",
    }
    response = requests.get(
        urljoin(settings.SELFSWAB_TURN_URL, f"/v1/contacts/{wa_id}/messages"),
        headers=headers,
    )
    response.raise_for_status()
    return response.json()


def get_whatsapp_media(media_id):
    headers = {"Authorization": f"Bearer {settings.SELFSWAB_TURN_TOKEN}"}
    response = requests.get(
        urljoin(settings.SELFSWAB_TURN_URL, f"v1/media/{media_id}"), headers=headers
    )
    response.raise_for_status()
    return response.content
