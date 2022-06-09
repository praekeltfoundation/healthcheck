# Generated by Django 3.1.14 on 2022-06-04 21:38

import django.contrib.gis.db.models.fields
from django.db import migrations, models
from django.contrib.postgres.operations import CreateExtension


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Location",
            fields=[
                ("name", models.CharField(max_length=100)),
                (
                    "location",
                    django.contrib.gis.db.models.fields.PointField(
                        geography=True, srid=4326
                    ),
                ),
                ("longitude", models.FloatField()),
                ("latitude", models.FloatField()),
                ("province", models.CharField(max_length=50)),
                (
                    "code",
                    models.CharField(max_length=50, primary_key=True, serialize=False),
                ),
                ("short_name", models.CharField(max_length=100)),
                ("address", models.CharField(max_length=255)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
