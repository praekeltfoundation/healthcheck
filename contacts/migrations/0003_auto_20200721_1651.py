# Generated by Django 2.2.13 on 2020-07-21 16:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("contacts", "0002_auto_20200721_1306"),
    ]

    operations = [
        migrations.AlterField(
            model_name="case",
            name="external_id",
            field=models.CharField(
                default="abecf62876cf480592c8b7baf449f1e0", max_length=255
            ),
        ),
    ]
