from .models import SelfSwabRegistration


def get_next_unique_contact_id():
    all_options = set(["CV%04dH" % i for i in range(1, 10000)])
    existing_contact_ids = set(
        SelfSwabRegistration.objects.values("contact_id")
        .distinct()
        .values_list("contact_id", flat=True)
    )

    try:
        contact_id = sorted(list(all_options - existing_contact_ids))[0]
    except IndexError:
        contact_id = "-1"

    return contact_id
