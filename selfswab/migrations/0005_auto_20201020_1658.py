# Generated by Django 3.1 on 2020-10-20 14:58

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("selfswab", "0004_auto_20201020_1640"),
    ]

    operations = [
        migrations.AlterField(
            model_name="selfswabscreen",
            name="timestamp",
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
