from urllib.parse import urljoin

import requests
from django.conf import settings
from phonenumber_field.serializerfields import PhoneNumberField
from rest_framework import serializers

LANGUAGES = {
    1: "eng",
    2: "zul",
    3: "afr",
    4: "xho",
    5: "nso",
    6: "sot",
    7: "ven",
    8: "tsn",
    9: "nbl",
    10: "ssw",
    11: "tso",
}

PROVINCES = {
    1: {
        "name": "Eastern Cape",
        "districts": {
            1: "Don't know",
            2: "Prefer not to say",
            3: "Buffalo City Metropolitan",
            4: "Nelson Mandela Bay",
            5: "Alfred Nzo",
            6: "Amathole",
            7: "Chris Hani",
            8: "Joe Gqaba",
            9: "OR Tambo",
            10: "Sarah Baartman",
        },
    },
    2: {
        "name": "Free State",
        "districts": {
            1: "Don't know",
            2: "Prefer not to say",
            11: "Mangaung",
            12: "Fezile Dabi",
            13: "Lejweleputswa",
            14: "Thabo Mofutsanyana",
            15: "Xhariep",
        },
    },
    3: {
        "name": "Gauteng",
        "districts": {
            1: "Don't know",
            2: "Prefer not to say",
            16: "City of Ekurhuleni",
            17: "City of Johannesburg",
            18: "City of Tshwane",
            19: "Sedibeng",
            20: "West Rand",
        },
    },
    4: {
        "name": "Kwazulu-natal",
        "districts": {
            1: "Don't know",
            2: "Prefer not to say",
            21: "eThekwini",
            22: "Amajuba",
            23: "Harry Gwala",
            24: "iLembe",
            25: "King Cetshwayo",
            26: "Ugu",
            27: "uMgungundlovu",
            28: "uMkhanyakude",
            29: "uMzinyathi",
            30: "uThukela",
            31: "Zululand",
        },
    },
    5: {
        "name": "Limpopo",
        "districts": {
            1: "Don't know",
            2: "Prefer not to say",
            32: "Capricorn",
            33: "Mopani",
            34: "Sekhukhune",
            35: "Vhembe",
            36: "Waterberg",
        },
    },
    6: {
        "name": "Mpumalanga",
        "districts": {
            1: "Don't know",
            2: "Prefer not to say",
            37: "Ehlanzeni",
            38: "Gert Sibande",
            39: "Nkangala",
        },
    },
    7: {
        "name": "Northern Cape",
        "districts": {
            1: "Don't know",
            2: "Prefer not to say",
            40: "Frances Baard",
            41: "John Taolo Gaetsewe",
            42: "Namakwa",
            43: "Pixley Ka Seme",
            44: "ZF Mgcawu",
        },
    },
    8: {
        "name": "North West",
        "districts": {
            1: "Don't know",
            2: "Prefer not to say",
            45: "Bojanala Platinum",
            46: "Dr Kenneth Kaunda",
            47: "Dr Ruth Segomotsi",
            48: "Ngaka Modiri Molema",
        },
    },
    9: {
        "name": "Western Cape",
        "districts": {
            1: "Don't know",
            2: "Prefer not to say",
            49: "City of Cape Town",
            50: "Cape Winelands",
            51: "Central Karoo",
            52: "Garden Route",
            53: "Overberg",
            54: "West Coast",
        },
    },
    10: {"name": "Outside SA", "districts": {1: "Don't know", 2: "Prefer not to say"}},
    11: {
        "name": "Prefer not to say",
        "districts": {1: "Don't know", 2: "Prefer not to say"},
    },
}

DISTRICTS = {}
for province in PROVINCES.values():
    for k, v in province["districts"].items():
        DISTRICTS[k] = v

GENDERS = {1: "Female", 2: "Male", 3: "Other", 4: "Prefer not to say"}

AGES = {
    2: "12-17 years",
    3: "18-34 years",
    4: "35-49 years",
    5: "50-59 years",
    6: "60 years and older",
    7: "Prefer not to say",
}


class RegistrationSerializer(serializers.Serializer):
    name = serializers.CharField()
    cell_no = PhoneNumberField()
    lang = serializers.ChoiceField(choices=list(LANGUAGES.items()))
    comms_choice = serializers.ChoiceField(choices=[(1, "WhatsApp")])
    email = serializers.EmailField(allow_blank=True, default="")
    popia_consent = serializers.ChoiceField(choices=[(0, "Yes")])
    province = serializers.ChoiceField(
        choices=[(k, v["name"]) for k, v in PROVINCES.items()],
        allow_null=True,
        default=None,
    )
    district = serializers.ChoiceField(
        choices=list(DISTRICTS.items()), allow_null=True, default=None
    )
    gender = serializers.ChoiceField(
        choices=list(GENDERS.items()), allow_null=True, default=None
    )
    age = serializers.ChoiceField(
        choices=list(AGES.items()), allow_null=True, default=None
    )

    def validate(self, data):
        """
        Check that district is in province
        """
        if not data.get("district"):
            return data
        if not data.get("province"):
            raise serializers.ValidationError(
                "province is required if district is provided"
            )
        province = PROVINCES[data["province"]]
        districts = list(province["districts"].keys())
        if data["district"] not in districts:
            raise serializers.ValidationError(f"district must be one of {districts}")
        return data

    def validate_cell_no(self, value):
        """
        Check that the number is a WhatsApp contact
        """
        response = requests.post(
            url=urljoin(settings.API_DOMAIN, "v1/contacts"),
            headers={
                "User-Agent": "healthcheck-django",
                "Authorization": f"Bearer {settings.TURN_API_KEY}",
                "Accept": "application/json",
            },
            json={"blocking": "wait", "contacts": [value.as_e164]},
        )
        response.raise_for_status()
        for contact in response.json()["contacts"]:
            if contact["status"] != "valid":
                raise serializers.ValidationError("not a WhatsApp contact")
        return value
