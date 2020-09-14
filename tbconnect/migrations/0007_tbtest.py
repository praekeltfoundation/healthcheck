# Generated by Django 3.1 on 2020-09-14 13:40

from django.db import migrations, models
import django.utils.timezone
import django_prometheus.models
import functools
import userprofile.validators
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ("tbconnect", "0006_auto_20200908_1655"),
    ]

    operations = [
        migrations.CreateModel(
            name="TBTest",
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
                    "deduplication_id",
                    models.CharField(default=uuid.uuid4, max_length=255, unique=True),
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
                    "result",
                    models.CharField(
                        choices=[
                            ("positive", "Positive"),
                            ("negative", "Negative"),
                            ("pending", "Pending"),
                        ],
                        max_length=10,
                    ),
                ),
                ("timestamp", models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
    ]
