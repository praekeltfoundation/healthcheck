# Generated by Django 3.1.14 on 2022-05-09 21:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("tbconnect", "0010_auto_20220509_1330"),
    ]

    operations = [
        migrations.RemoveField(model_name="tbcheck", name="group_arm",),
    ]