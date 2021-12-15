from django.contrib import admin
from real411.models import Complaint


@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    pass
