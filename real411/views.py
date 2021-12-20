from django.shortcuts import get_object_or_404
from real411.models import Complaint
from real411.serializers import ComplaintSerializer, ComplaintUpdateSerializer
from rest_framework import viewsets, permissions
from userprofile.views import CursorPaginationFactory
from rest_framework.response import Response


class DjangoModelViewPermissions(permissions.DjangoModelPermissions):
    """
    DjangoModelPermissions, but with added restrictions on viewing data according to the
    view permission
    """

    perms_map = {
        "GET": ["%(app_label)s.view_%(model_name)s"],
        "OPTIONS": ["%(app_label)s.view_%(model_name)s"],
        "HEAD": ["%(app_label)s.view_%(model_name)s"],
        "POST": ["%(app_label)s.add_%(model_name)s"],
        "PUT": ["%(app_label)s.change_%(model_name)s"],
        "PATCH": ["%(app_label)s.change_%(model_name)s"],
        "DELETE": ["%(app_label)s.delete_%(model_name)s"],
    }


class ComplaintViewSet(viewsets.ModelViewSet):
    queryset = Complaint.objects.all()
    serializer_class = ComplaintSerializer
    permission_classes = [DjangoModelViewPermissions]
    pagination_class = CursorPaginationFactory("id")


class ComplaintUpdateViewSet(viewsets.ViewSet):
    serializer_class = ComplaintUpdateSerializer

    def create(self, request):
        serializer = ComplaintUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        complaint = get_object_or_404(
            Complaint, complaint_ref=serializer.validated_data["complaint_ref"]
        )
        # TODO: run background task to notify update
        return Response()
