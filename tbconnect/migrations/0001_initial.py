# Generated by Django 3.1 on 2020-08-25 11:07

import functools
import uuid

from django.db import migrations, models

import userprofile.validators


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="TBCheck",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "created_by",
                    models.CharField(blank=True, default="", max_length=255),
                ),
                (
                    "msisdn",
                    models.CharField(
                        max_length=255,
                        validators=[
                            functools.partial(
                                userprofile.validators._phone_number,
                                *(),
                                **{"country": "ZA"}
                            )
                        ],
                    ),
                ),
                ("source", models.CharField(max_length=255)),
                (
                    "province",
                    models.CharField(
                        choices=[
                            ("ZA-EC", "Eastern Cape"),
                            ("ZA-FS", "Free State"),
                            ("ZA-GT", "Gauteng"),
                            ("ZA-LP", "Limpopo"),
                            ("ZA-MP", "Mpumalanga"),
                            ("ZA-NC", "Northern Cape"),
                            ("ZA-NL", "Kwazulu-Natal"),
                            ("ZA-NW", "North-West (South Africa)"),
                            ("ZA-WC", "Western Cape"),
                        ],
                        max_length=6,
                    ),
                ),
                ("city", models.CharField(max_length=255)),
                (
                    "age",
                    models.CharField(
                        choices=[
                            ("<18", "<18"),
                            ("18-40", "18-40"),
                            ("40-65", "40-65"),
                            (">65", ">65"),
                        ],
                        max_length=5,
                    ),
                ),
                (
                    "gender",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("male", "Male"),
                            ("female", "Female"),
                            ("other", "Other"),
                            ("not_say", "Rather not say"),
                        ],
                        default="",
                        max_length=7,
                    ),
                ),
                (
                    "location",
                    models.CharField(
                        blank=True,
                        default="",
                        max_length=255,
                        validators=[userprofile.validators.geographic_coordinate],
                    ),
                ),
                (
                    "cough",
                    models.CharField(
                        choices=[
                            ("no", "No"),
                            ("yes_lt_2weeks", "Yes, less than 2 weeks"),
                            ("yes_gt_2weeks", "Yes, more than 2 weeks"),
                        ],
                        max_length=13,
                    ),
                ),
                ("fever", models.BooleanField()),
                ("sweat", models.BooleanField()),
                ("weight", models.BooleanField()),
                (
                    "exposure",
                    models.CharField(
                        choices=[
                            ("yes", "Yes"),
                            ("no", "No"),
                            ("not_sure", "Not sure"),
                        ],
                        max_length=9,
                    ),
                ),
                (
                    "tracing",
                    models.BooleanField(
                        help_text="Whether the NDoH can contact the user"
                    ),
                ),
            ],
        ),
    ]
