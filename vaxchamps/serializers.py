from urllib.parse import urljoin

import requests
from django.conf import settings
from phonenumber_field.serializerfields import PhoneNumberField
from rest_framework import serializers

LANGUAGES = {
    "eng": 1,
    "zul": 2,
    "afr": 3,
    "xho": 4,
    "nso": 5,
    "sot": 6,
    "ven": 7,
    "tsn": 8,
    "nbl": 9,
    "ssw": 10,
    "tso": 11,
}

PROVINCES = {
    "Eastern Cape": {
        "id": 1,
        "districts": {
            "Don't know": 1,
            "Prefer not to say": 2,
            "Buffalo City Metropolitan": 3,
            "Nelson Mandela Bay": 4,
            "Alfred Nzo": 5,
            "Amathole": 6,
            "Chris Hani": 7,
            "Joe Gqaba": 8,
            "OR Tambo": 9,
            "Sarah Baartman": 10,
        },
    },
    "Free State": {
        "id": 2,
        "districts": {
            "Don't know": 1,
            "Prefer not to say": 2,
            "Mangaung": 11,
            "Fezile Dabi": 12,
            "Lejweleputswa": 13,
            "Thabo Mofutsanyana": 14,
            "Xhariep": 15,
        },
    },
    "Gauteng": {
        "id": 3,
        "districts": {
            "Don't know": 1,
            "Prefer not to say": 2,
            "City of Ekurhuleni": 16,
            "City of Johannesburg": 17,
            "City of Tshwane": 18,
            "Sedibeng": 19,
            "West Rand": 20,
        },
    },
    "Kwazulu-natal": {
        "id": 4,
        "districts": {
            "Don't know": 1,
            "Prefer not to say": 2,
            "eThekwini": 21,
            "Amajuba": 22,
            "Harry Gwala": 23,
            "iLembe": 24,
            "King Cetshwayo": 25,
            "Ugu": 26,
            "uMgungundlovu": 27,
            "uMkhanyakude": 28,
            "uMzinyathi": 29,
            "uThukela": 30,
            "Zululand": 31,
        },
    },
    "Limpopo": {
        "id": 5,
        "districts": {
            "Don't know": 1,
            "Prefer not to say": 2,
            "Capricorn": 32,
            "Mopani": 33,
            "Sekhukhune": 34,
            "Vhembe": 35,
            "Waterberg": 36,
        },
    },
    "Mpumalanga": {
        "id": 6,
        "districts": {
            "Don't know": 1,
            "Prefer not to say": 2,
            "Ehlanzeni": 37,
            "Gert Sibande": 38,
            "Nkangala": 39,
        },
    },
    "Northern Cape": {
        "id": 7,
        "districts": {
            "Don't know": 1,
            "Prefer not to say": 2,
            "Frances Baard": 40,
            "John Taolo Gaetsewe": 41,
            "Namakwa": 42,
            "Pixley Ka Seme": 43,
            "ZF Mgcawu": 44,
        },
    },
    "North West": {
        "id": 8,
        "districts": {
            "Don't know": 1,
            "Prefer not to say": 2,
            "Bojanala Platinum": 45,
            "Dr Kenneth Kaunda": 46,
            "Dr Ruth Segomotsi": 47,
            "Ngaka Modiri Molema": 48,
        },
    },
    "Western Cape": {
        "id": 9,
        "districts": {
            "Don't know": 1,
            "Prefer not to say": 2,
            "City of Cape Town": 49,
            "Cape Winelands": 50,
            "Central Karoo": 51,
            "Garden Route": 52,
            "Overberg": 53,
            "West Coast": 54,
        },
    },
    "Outside SA": {"id": 10, "districts": {"Don't know": 1, "Prefer not to say": 2}},
    "Prefer not to say": {
        "id": 11,
        "districts": {"Don't know": 1, "Prefer not to say": 2},
    },
}

DISTRICTS = {}
for province in PROVINCES.values():
    for k, v in province["districts"].items():
        DISTRICTS[k] = v

GENDERS = {"Female": 1, "Male": 2, "Other": 3, "Prefer not to say": 4}

AGES = {
    "12-17 years": 2,
    "18-34 years": 3,
    "35-49 years": 4,
    "50-59 years": 5,
    "60 years and older": 6,
    "Prefer not to say": 7,
}


class RegistrationSerializer(serializers.Serializer):
    name = serializers.CharField()
    cell_no = PhoneNumberField()
    lang = serializers.ChoiceField(choices=[(v, k) for k, v in LANGUAGES.items()])
    comms_choice = serializers.ChoiceField(choices=[(1, "WhatsApp")])
    email = serializers.EmailField(allow_blank=True, default="")
    popia_consent = serializers.ChoiceField(choices=[(0, "Yes")])
    province = serializers.ChoiceField(
        choices=[(v["id"], k) for k, v in PROVINCES.items()],
        allow_null=True,
        default=None,
    )
    district = serializers.ChoiceField(
        choices=[(v, k) for k, v in DISTRICTS.items()], allow_null=True, default=None
    )
    gender = serializers.ChoiceField(
        choices=[(v, k) for k, v in GENDERS.items()], allow_null=True, default=None
    )
    age = serializers.ChoiceField(
        choices=[(v, k) for k, v in AGES.items()], allow_null=True, default=None
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
        province = {v["id"]: v for v in PROVINCES.values()}[data["province"]]
        districts = [v for v in province["districts"].values()]
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
