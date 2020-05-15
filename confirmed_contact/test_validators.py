from django.core.exceptions import ValidationError
from django.test import SimpleTestCase

from confirmed_contact import validators


class PhoneNumberValidatorTests(SimpleTestCase):
    def test_parse_error(self):
        """
        Should raise a ValidationError if we cannot parse
        """
        self.assertRaisesMessage(
            ValidationError,
            "The string supplied did not seem to be a phone number",
            validators.za_phone_number,
            "invalid",
        )

    def test_not_possible(self):
        """
        Should raise a ValidationError if the number is not possible
        """
        self.assertRaisesMessage(
            ValidationError,
            "Not a possible phone number",
            validators.za_phone_number,
            "+123",
        )

    def test_not_valid(self):
        """
        Should raise a ValidationError if the number is not valid
        """
        self.assertRaisesMessage(
            ValidationError,
            "Not a valid phone number",
            validators.za_phone_number,
            "+12001230101",
        )
