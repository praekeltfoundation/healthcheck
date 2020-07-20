from itertools import chain

from django.shortcuts import render
# from collections import OrderedDict
from rest_framework import generics, permissions, status
from rest_framework.response import Response

from .serializers import CaseSerializer, ContactSerializer


class ConfirmedContactView(generics.GenericAPIView):
    """
    POST endpoint to create a case and contact.
    ---
    POST fields:
    * msisdn
    * timestamp
    * external_id (UUID4)
    - name (optional)
    - case_id (optional)
    """

    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = ContactSerializer

    def post(self, request, *args, **kwargs):
        data = request.data

        contact_serializer = ContactSerializer(
            data={
                "msisdn": data.pop("msisdn", None),
                "external_id": data.pop("external_id", None),
            }
        )

        contact_serializer.is_valid(raise_exception=True)
        contact = contact_serializer.save()

        case_serializer = CaseSerializer(data=data)
        case_serializer.is_valid(raise_exception=True)
        case = case_serializer.save()

        case.created_by = self.request.user
        case.save(
            update_fields=["created_by",]
        )

        contact.cases.add(case)

        print(
            ContactSerializer(instance=contact).data, CaseSerializer(instance=case).data
        )
        print(contact_serializer, case_serializer)

        return Response(
            {
                **ContactSerializer(instance=contact).data,
                **CaseSerializer(instance=case).data,
            },
            status=status.HTTP_201_CREATED,
        )
