import functools

import phonenumbers
from iso6709 import Location
from rest_framework.serializers import ValidationError


def geographic_coordinate(value):
    try:
        Location(value)
    except AttributeError:
        raise ValidationError("Invalid ISO6709 geographic coordinate")


def _phone_number(value, country):
    try:
        number = phonenumbers.parse(value, country)
    except phonenumbers.NumberParseException as e:
        raise ValidationError(str(e))
    if not phonenumbers.is_possible_number(number):
        raise ValidationError("Not a possible phone number")
    if not phonenumbers.is_valid_number(number):
        raise ValidationError("Not a valid phone number")


za_phone_number = functools.partial(_phone_number, country="ZA")
