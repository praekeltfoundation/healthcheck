# Generated by Django 3.1.13 on 2021-12-10 11:04

import datetime

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("covid_cases", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="SACoronavirusCounter",
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
                    "tests",
                    models.PositiveIntegerField(help_text="Total tests completed"),
                ),
                (
                    "positive",
                    models.PositiveIntegerField(
                        help_text="Total positive cases identified"
                    ),
                ),
                (
                    "recoveries",
                    models.PositiveIntegerField(help_text="Total recoveries"),
                ),
                ("deaths", models.PositiveIntegerField(help_text="Total deaths")),
                (
                    "vaccines",
                    models.PositiveIntegerField(
                        help_text="Total vaccines administered"
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
            ],
        ),
        migrations.AddConstraint(
            model_name="sacoronaviruscounter",
            constraint=models.UniqueConstraint(
                fields=("date",), name="unique_counters"
            ),
        ),
    ]
