from django.db.utils import IntegrityError
from rest_framework import generics, permissions, status
from rest_framework.response import Response

from .models import Case, Contact
from .serializers import CaseSerializer, ContactSerializer
from .tasks import send_contact_update


class ConfirmedContactView(generics.GenericAPIView):
    """
    POST endpoint to create a case and contact.
    ---
    POST fields:
    * msisdn
    * timestamp
    * external_id
    - name (optional)
    - case_id (optional)
    ---
    Response example:
    ```
    {
        "id": "84fe2a6c-a5f8-4994-9d96-d765514740b3",
        "msisdn": "+27820001001",
        "date_start": "2020-07-19T19:35:11.400070Z",
        "case_id": null,
        "name": null,
        "created_by": "admin",
        "created_at": "2020-07-21T13:09:06.921305Z",
        "external_id": "51e7f725b59442c7b75b48752b29f243"
    }
    ```
    """

    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        data = request.data

        msisdn = data.pop("msisdn", None)

        # Try to create a contact

        contact_query = Contact.objects.filter(msisdn=msisdn)
        if contact_query.exists():
            contact = contact_query.first()
        else:
            try:
                contact_serializer = ContactSerializer(data={"msisdn": msisdn})
                contact_serializer.is_valid(raise_exception=True)
                contact = contact_serializer.save()
            except IntegrityError:
                contact = Contact.objects.get(msisdn=msisdn)
                # race condition - pull existing contact

        case_query = Case.objects.filter(external_id=data.get("external_id")).exists()
        if case_query:
            return Response({"status": "ALREADY_EXISTS"}, status=status.HTTP_200_OK,)
        else:
            try:
                case_serializer = CaseSerializer(data=data)
                case_serializer.is_valid(raise_exception=True)
                case = case_serializer.save()
            except IntegrityError:
                # race condition - raise error
                return Response(
                    {"status": "ALREADY_EXISTS"}, status=status.HTTP_200_OK,
                )

        # deactivate existing cases with earlier timestamp
        Case.objects.filter(contact=contact, date_start__lte=case.date_start,).exclude(
            id=case.id,
        ).update(is_active=False)

        # deactivate case if it is not the latest for current contact
        if Case.objects.filter(
            contact=contact, date_start__gt=case.date_start,
        ).exists():
            case.is_active = False
            case.save(update_fields=("is_active",))

        case.created_by = self.request.user
        case.contact = contact
        case.save(update_fields=("created_by", "contact",))

        if case.is_active:
            # dispatch first notification task
            # but ONLY if case.is_active is True

            send_contact_update.delay(
                phone_number=str(case.contact.msisdn),
                confirmed_contact=True,
                case_id=case.id,
            )

        return Response(
            {
                **ContactSerializer(instance=contact).data,
                **CaseSerializer(instance=case).data,
            },
            status=status.HTTP_201_CREATED,
        )
