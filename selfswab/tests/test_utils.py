from django.test import TestCase

from selfswab.utils import is_barcode_format_valid


class IsBarcodeFormatValidTests(TestCase):
    def test_is_barcode_format_valid(self):
        self.assertFalse(is_barcode_format_valid("123"))
        self.assertFalse(is_barcode_format_valid("CP123"))
        self.assertTrue(is_barcode_format_valid("CP159600000"))
        self.assertFalse(is_barcode_format_valid("CP159601101"))
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
