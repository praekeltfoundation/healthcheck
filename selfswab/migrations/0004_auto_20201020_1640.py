# Generated by Django 3.1 on 2020-10-20 14:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("selfswab", "0003_auto_20201020_1613"),
    ]

    operations = [
        migrations.AddField(
            model_name="selfswabscreen",
            name="created_by",
            field=models.CharField(blank=True, default="", max_length=255),
        ),
        migrations.AddField(
            model_name="selfswabtest",
            name="created_by",
            field=models.CharField(blank=True, default="", max_length=255),
        ),
    ]
