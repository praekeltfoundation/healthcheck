from rest_framework import generics, permissions, status
from rest_framework.response import Response

from .models import Case, Contact
from .serializers import CaseSerializer, ContactSerializer


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
        "date_start": "2020-07-23T19:35:11.400070Z",
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

        external_id = data.get("external_id", None)

        # look up whether Case exists
        if (
            external_id is not None
            and Case.objects.filter(  # noqa: W503, E261
                external_id=external_id
            ).exists()
        ):
            return Response({"status": "ALREADY_EXISTS"}, status=status.HTTP_200_OK,)

        msisdn = data.pop("msisdn", None)

        # look up whether Contact exists;
        # create or retrieve;
        # attach to Case.
        if msisdn is not None and not Contact.objects.filter(msisdn=msisdn).exists():

            contact_serializer = ContactSerializer(data={"msisdn": msisdn})

            contact_serializer.is_valid(raise_exception=True)
            contact = contact_serializer.save()
        else:
            contact = Contact.objects.filter(msisdn=msisdn).first()

        # deactivate existing cases
        Case.objects.filter(contact=contact).update(is_active=False)

        case_serializer = CaseSerializer(data=data)
        case_serializer.is_valid(raise_exception=True)
        case = case_serializer.save()

        case.created_by = self.request.user
        case.contact = contact
        case.save(update_fields=("created_by", "contact",))

        # TODO: dispatch first notification task

        return Response(
            {
                **ContactSerializer(instance=contact).data,
                **CaseSerializer(instance=case).data,
            },
            status=status.HTTP_201_CREATED,
        )
