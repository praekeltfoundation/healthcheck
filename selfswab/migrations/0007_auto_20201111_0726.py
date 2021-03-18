# Generated by Django 3.1 on 2020-11-11 05:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("selfswab", "0006_auto_20201110_1455"),
    ]

    operations = [
        migrations.AlterField(
            model_name="selfswabtest",
            name="result",
            field=models.CharField(
                choices=[
                    ("Pending", "Pending"),
                    ("Positive", "Positive"),
                    ("Negative", "Negative"),
                    ("Rejected", "Rejected"),
                    ("Invalid", "Invalid"),
                    ("Equivocal", "Equivocal"),
                    ("Inconclusive", "Inconclusive"),
                    ("Indeterminate", "Indeterminate"),
                    ("Error", "Error"),
                ],
                default="Pending",
                max_length=100,
            ),
        ),
    ]