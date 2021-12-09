# Generated by Django 3.1.13 on 2021-12-09 15:12

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="District",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        blank=True,
                        help_text="District name, eg. City of Cape Town Metro",
                        max_length=50,
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True,
                        help_text="When this was added to the database",
                    ),
                ),
                (
                    "updated_at",
                    models.DateTimeField(
                        auto_now=True, help_text="When this was last updated"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Province",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        blank=True,
                        help_text="Province name, eg. Western Cape",
                        max_length=50,
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True,
                        help_text="When this was added to the database",
                    ),
                ),
                (
                    "updated_at",
                    models.DateTimeField(
                        auto_now=True, help_text="When this was last updated"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="SubDistrict",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        help_text="Sub District name, eg. Northerm Health sub-District",
                        max_length=50,
                    ),
                ),
                (
                    "subdistrict_id",
                    models.PositiveIntegerField(
                        help_text="The ID of this sub district", null=True
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True,
                        help_text="When this was added to the database",
                    ),
                ),
                (
                    "updated_at",
                    models.DateTimeField(
                        auto_now=True, help_text="When this was last updated"
                    ),
                ),
                (
                    "district",
                    models.ForeignKey(
                        blank=True,
                        help_text="The parent district of this sub district",
                        on_delete=django.db.models.deletion.CASCADE,
                        to="covid_cases.district",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Ward",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("ward_id", models.CharField(blank=True, max_length=80)),
                ("ward_number", models.CharField(blank=True, max_length=80)),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True,
                        help_text="When this was added to the database",
                    ),
                ),
                (
                    "updated_at",
                    models.DateTimeField(
                        auto_now=True, help_text="When this was last updated"
                    ),
                ),
                (
                    "sub_district",
                    models.ForeignKey(
                        help_text="The parent sub district of this ward",
                        on_delete=django.db.models.deletion.CASCADE,
                        to="covid_cases.subdistrict",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="WardCase",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "object_id",
                    models.PositiveIntegerField(help_text="Unique ID for this entry"),
                ),
                ("male", models.PositiveIntegerField(help_text="Number of male cases")),
                (
                    "female",
                    models.PositiveIntegerField(help_text="Number of female cases"),
                ),
                (
                    "unknown_gender",
                    models.PositiveIntegerField(
                        help_text="Number of cases where the gender is unknown"
                    ),
                ),
                (
                    "age_1_10",
                    models.PositiveIntegerField(
                        help_text="Number of cases for the 1-10 years age group"
                    ),
                ),
                (
                    "age_11_20",
                    models.PositiveIntegerField(
                        help_text="Number of cases for the 11-20 years age group"
                    ),
                ),
                (
                    "age_21_30",
                    models.PositiveIntegerField(
                        help_text="Number of cases for the 21-30 years age group"
                    ),
                ),
                (
                    "age_31_40",
                    models.PositiveIntegerField(
                        help_text="Number of cases for the 31-40 years age group"
                    ),
                ),
                (
                    "age_41_50",
                    models.PositiveIntegerField(
                        help_text="Number of cases for the 41-50 years age group"
                    ),
                ),
                (
                    "age_51_60",
                    models.PositiveIntegerField(
                        help_text="Number of cases for the 51-60 years age group"
                    ),
                ),
                (
                    "age_61_70",
                    models.PositiveIntegerField(
                        help_text="Number of cases for the 61-70 years age group"
                    ),
                ),
                (
                    "age_71_80",
                    models.PositiveIntegerField(
                        help_text="Number of cases for the 71-80 years age group"
                    ),
                ),
                (
                    "age_81",
                    models.PositiveIntegerField(
                        help_text="Number of cases for the >=81 years age group"
                    ),
                ),
                (
                    "unknown_age",
                    models.PositiveIntegerField(
                        help_text="Number of cases where the age is unknown"
                    ),
                ),
                (
                    "latest",
                    models.PositiveIntegerField(help_text="Number of new cases today"),
                ),
                (
                    "total_number_of_cases",
                    models.PositiveIntegerField(
                        help_text="Total number of cases for this ward"
                    ),
                ),
                (
                    "date",
                    models.DateField(
                        default=datetime.date.today, help_text="The day the data is for"
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True,
                        help_text="When this was added to the database",
                    ),
                ),
                (
                    "updated_at",
                    models.DateTimeField(
                        auto_now=True, help_text="When this was last updated"
                    ),
                ),
                (
                    "ward",
                    models.ForeignKey(
                        help_text="Ward that this data is for",
                        on_delete=django.db.models.deletion.CASCADE,
                        to="covid_cases.ward",
                    ),
                ),
            ],
        ),
        migrations.AddConstraint(
            model_name="province",
            constraint=models.UniqueConstraint(
                fields=("name",), name="unique_province"
            ),
        ),
        migrations.AddField(
            model_name="district",
            name="province",
            field=models.ForeignKey(
                help_text="The parent province of this district",
                on_delete=django.db.models.deletion.CASCADE,
                to="covid_cases.province",
            ),
        ),
        migrations.AddConstraint(
            model_name="wardcase",
            constraint=models.UniqueConstraint(
                fields=("date", "object_id"), name="unique_entries"
            ),
        ),
        migrations.AddConstraint(
            model_name="ward",
            constraint=models.UniqueConstraint(
                fields=("sub_district", "ward_id", "ward_number"), name="unique_ward"
            ),
        ),
        migrations.AddConstraint(
            model_name="subdistrict",
            constraint=models.UniqueConstraint(
                fields=("district", "name", "subdistrict_id"), name="unique_subdistrict"
            ),
        ),
        migrations.AddConstraint(
            model_name="district",
            constraint=models.UniqueConstraint(
                fields=("province", "name"), name="unique_district"
            ),
        ),
    ]
