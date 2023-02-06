from .models import TBCheck, TBTest


def run():
    # Get all TB tests
    tbtests = TBTest.objects.all()

    for tbtest in tbtests:
        # Get recent tbcheck to update tbtest source
        print(
            "Contact: ", tbtest.msisdn
        )  # To test in QA AttributeError: 'NoneType' object has no attribute 'source'
        tbcheck = (
            TBCheck.objects.filter(
                msisdn=tbtest.msisdn, completed_timestamp__lt=tbtest.timestamp
            )
            .order_by("-completed_timestamp")
            .first()
        )
        print("TBcheck", tbcheck.msisdn, tbcheck.source)
        if tbcheck.source == "USSD" and tbtest.source != "SMS":
            # Update mismatching test to sms
            tbtest.source = "SMS"
            tbtest.save()

    print("Script Completed")
