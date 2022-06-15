# Generated by Django 3.1.14 on 2022-06-15 11:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("tbconnect", "0013_auto_20220517_1323"),
    ]

    operations = [
        migrations.AddField(
            model_name="tbcheck",
            name="clinic_to_visit",
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name="tbcheck",
            name="clinic_visit_day",
            field=models.CharField(
                blank=True,
                choices=[
                    ("mon", "Monday"),
                    ("tue", "Tuesday"),
                    ("wed", "Wednesday"),
                    ("thu", "Thursday"),
                    ("fri", "Friday"),
                ],
                max_length=3,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="tbcheck",
            name="research_consent",
            field=models.BooleanField(blank=True, null=True),
        ),
    ]