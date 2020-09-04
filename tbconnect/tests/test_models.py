from django.test import TestCase
from tbconnect.models import TBCheck


class TBCheckTest(TestCase):
    def create_check(self, source, risk, optin=True):
        return TBCheck.objects.create(
            **{
                "msisdn": "+123",
                "fever": True,
                "sweat": True,
                "weight": True,
                "tracing": True,
                "source": source,
                "risk": risk,
                "follow_up_optin": optin,
            }
        )

    def test_should_sync_to_rapidpro(self):
        # Checks from USSD always goes to Rapidpro, regardless of risk or optin
        check = self.create_check("USSD", TBCheck.RISK_LOW)
        self.assertTrue(check.should_sync_to_rapidpro)

        check = self.create_check("USSD", TBCheck.RISK_MODERATE_WITH_COUGH)
        self.assertTrue(check.should_sync_to_rapidpro)

        check = self.create_check("USSD", TBCheck.RISK_MODERATE_WITHOUT_COUGH)
        self.assertTrue(check.should_sync_to_rapidpro)

        check = self.create_check("USSD", TBCheck.RISK_HIGH)
        self.assertTrue(check.should_sync_to_rapidpro)

        # Checks from WhatsApp only goes to rapidpro if not low risk and opted in
        check = self.create_check("WhatsApp", TBCheck.RISK_LOW)
        self.assertFalse(check.should_sync_to_rapidpro)

        check = self.create_check("WhatsApp", TBCheck.RISK_HIGH)
        self.assertTrue(check.should_sync_to_rapidpro)

        check = self.create_check("WhatsApp", TBCheck.RISK_MODERATE_WITH_COUGH)
        self.assertTrue(check.should_sync_to_rapidpro)

        check = self.create_check("WhatsApp", TBCheck.RISK_MODERATE_WITHOUT_COUGH)
        self.assertTrue(check.should_sync_to_rapidpro)

        check = self.create_check(
            "WhatsApp", TBCheck.RISK_MODERATE_WITHOUT_COUGH, False
        )
        self.assertFalse(check.should_sync_to_rapidpro)
