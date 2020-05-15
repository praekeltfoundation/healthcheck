from django.contrib import admin
from django.core.paginator import Paginator
from django.db import OperationalError, connection, transaction
from django import forms
from django.urls import path
from django.template.response import TemplateResponse
from django.shortcuts import redirect
from django.utils.functional import cached_property
import csv

from confirmed_contact.models import ConfirmedContact


class ApproximatePaginator(Paginator):
    """
    Paginator that returns an approximate count if doing the real count takes too long
    A mix between:
    https://hakibenita.com/optimizing-the-django-admin-paginator
    https://wiki.postgresql.org/wiki/Count_estimate
    """

    @cached_property
    def count(self):
        cursor = connection.cursor()
        with transaction.atomic(), connection.cursor() as cursor:
            cursor.execute("SET LOCAL statement_timeout TO 50")
            try:
                return super().count
            except OperationalError:
                pass
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT reltuples FROM pg_class WHERE relname = %s",
                [self.object_list.query.model._meta.db_table],
            )
            return int(cursor.fetchone()[0])


class CsvImportForm(forms.Form):
    csv_file = forms.FileField()


@admin.register(ConfirmedContact)
class ConfirmedContactAdmin(admin.ModelAdmin):
    sortable_by = "msisdn"
    paginator = ApproximatePaginator
    show_full_result_count = False
    list_display = ("msisdn", "timestamp")
    search_fields = ("msisdn",)
    readonly_fields = ("created_by", "created_at")
    change_list_template = "confirmed_contact_changelist.html"

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [path("import_csv/", self.import_csv)]
        return my_urls + urls

    @transaction.atomic
    def _process_csv(self, request, f):
        decoded = f.read().decode("utf-8").splitlines()
        reader = csv.DictReader(decoded)
        objects = []
        for row in reader:
            cc = ConfirmedContact(**row)
            cc.created_by = request.user.username
            objects.append(cc)
        ConfirmedContact.objects.bulk_create(objects, ignore_conflicts=True)
        self.message_user(request, "CSV import successful")

    def import_csv(self, request):
        if request.method == "POST":
            form = CsvImportForm(request.POST, request.FILES)
            if form.is_valid():
                # If there are errors in the CSV, fail and report to sentry. This
                # import is for internal use only
                self._process_csv(request, request.FILES["csv_file"])
                return redirect("..")
        else:
            form = CsvImportForm()
        context = dict(self.admin_site.each_context(request), form=form)
        return TemplateResponse(request, "csv_form.html", context)

    def save_model(self, request, obj, form, change):
        obj.created_by = request.user.username
        super().save_model(request, obj, form, change)
