# Generated by Django 3.1 on 2020-09-02 18:08

import django.contrib.postgres.indexes
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("userprofile", "0009_healthcheckuserprofile_language"),
    ]

    operations = [
        migrations.AddIndex(
            model_name="healthcheckuserprofile",
            index=django.contrib.postgres.indexes.GinIndex(
                fields=["data"], name="userprofile__data__gin_idx"
            ),
        ),
    ]
