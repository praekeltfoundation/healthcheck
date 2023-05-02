from userprofile.models import HealthCheckUserProfile


def create_user_profile(
    msisdn="+27821234567",
    gender="female",
    province="ZA-GP",
    research_consent=True,
    activation=None,
    tbconnect_group_arm=None,
):
    return HealthCheckUserProfile.objects.create(
        msisdn=msisdn,
        language="eng",
        gender=gender,
        province=province,
        activation=activation,
        research_consent=research_consent,
        tbconnect_group_arm=tbconnect_group_arm,
    )
