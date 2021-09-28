from django.test import TestCase
from tbconnect.serializers import TBCheckSerializer


class TBCheckSerializerTests(TestCase):
    def test_valid_tbcheck(self):
        """
        If age is <18 skip location and location_
        """
        data = {
            "msisdn": "+2349039756628",
            "source": "WhatsApp",
            "province": "ZA-GT",
            "city": "<not collected>",
            "age": "<18",
            "gender": "male",
            "cough": "True",
            "fever": "False",
            "sweat": "False",
            "weight": "False",
            "exposure": "no",
            "tracing": "False",
            "risk": "low",
        }
        serializer = TBCheckSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(
            dict(serializer.validated_data),
            {
                "age": "<18",
                "city": "<not collected>",
                "cough": True,
                "exposure": "no",
                "fever": False,
                "gender": "male",
                "msisdn": "+2349039756628",
                "province": "ZA-GT",
                "risk": "low",
                "source": "WhatsApp",
                "sweat": False,
                "tracing": False,
                "weight": False,
            },
        )
