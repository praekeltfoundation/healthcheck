# Generated by Django 3.1 on 2020-10-29 08:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("selfswab", "0003_selfswabregistration"),
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
                ],
                default="Pending",
                max_length=100,
            ),
        ),
    ]
