# Generated by Django 3.1.14 on 2022-05-11 15:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("userprofile", "0011_healthcheckuserprofile_tbconnect_group_arm"),
    ]

    operations = [
        migrations.AddField(
            model_name="healthcheckuserprofile",
            name="research_consent",
            field=models.BooleanField(null=True),
        ),
    ]