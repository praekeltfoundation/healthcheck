# Generated by Django 2.2.13 on 2020-07-21 13:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("contacts", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(model_name="contact", name="cases",),
        migrations.AddField(
            model_name="case",
            name="contact",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="cases",
                to="contacts.Contact",
            ),
        ),
        migrations.AddField(
            model_name="case",
            name="external_id",
            field=models.CharField(
                default="adf7a5b7df7f426a921c0921a02775ff", max_length=255
            ),
        ),
        migrations.AlterField(
            model_name="case",
            name="date_notification",
            field=models.DateTimeField(null=True),
        ),
    ]
