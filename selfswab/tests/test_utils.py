import json
import responses

from django.test import TestCase, override_settings

from selfswab.utils import (
    is_barcode_format_valid,
    upload_turn_media,
    send_whatsapp_media_message,
)


class IsBarcodeFormatValidTests(TestCase):
    def test_is_barcode_format_valid(self):
        self.assertFalse(is_barcode_format_valid("123"))
        self.assertFalse(is_barcode_format_valid("CP123"))
        self.assertTrue(is_barcode_format_valid("CP159600000"))
        self.assertTrue(is_barcode_format_valid("CP159601101"))
        self.assertFalse(is_barcode_format_valid("CP158600001"))

        self.assertTrue(is_barcode_format_valid("CP159600001"))
        self.assertTrue(is_barcode_format_valid("CP159600055"))
        self.assertTrue(is_barcode_format_valid("CP159600100"))

        self.assertTrue(is_barcode_format_valid("CP999T99000"))
        self.assertFalse(is_barcode_format_valid("CP999T99101"))
        self.assertFalse(is_barcode_format_valid("CP998T99001"))

        self.assertTrue(is_barcode_format_valid("CP999T99001"))
        self.assertTrue(is_barcode_format_valid("CP999T99055"))
        self.assertTrue(is_barcode_format_valid("CP999T99100"))

        self.assertTrue(is_barcode_format_valid("CP1596100504"))


class UploadTurnMediaTests(TestCase):
    @responses.activate
    @override_settings(
        SELFSWAB_TURN_URL="https://turn.io",
        SELFSWAB_TURN_TOKEN="321",
    )
    def test_upload_turn_media(self):

        responses.add(
            responses.POST,
            "https://turn.io/v1/media",
            json={"media": [{"id": "media-uuid"}]},
        )

        self.assertEqual(upload_turn_media("fake pdf"), "media-uuid")

        [call] = responses.calls

        self.assertEqual(call.request.body, "fake pdf")

        self.assertEqual(call.request.headers["Authorization"], "Bearer 321")
        self.assertEqual(call.request.headers["Content-Type"], "application/pdf")


class SendWhatsAppMediaTests(TestCase):
    @responses.activate
    @override_settings(
        SELFSWAB_TURN_URL="https://turn.io",
        SELFSWAB_TURN_TOKEN="321",
    )
    def test_send_whatsapp_media_message(self):
        responses.add(
            responses.POST,
            "https://turn.io/v1/messages",
            json={"messages": [{"id": "gBEGkYiEB1VXAglK1ZEqA1YKPrU"}]},
        )

        send_whatsapp_media_message("27123", "document", "media-uuid")

        [call] = responses.calls

        self.assertEqual(
            json.loads(call.request.body),
            {
                "recipient_type": "individual",
                "to": "27123",
                "type": "document",
                "document": {"id": "media-uuid"},
            },
        )

        self.assertEqual(call.request.headers["Authorization"], "Bearer 321")
        self.assertEqual(call.request.headers["Content-Type"], "application/json")
