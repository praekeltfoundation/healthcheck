# Generated by Django 3.1.14 on 2022-05-11 15:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tbconnect', '0011_remove_tbcheck_group_arm'),
    ]

    operations = [
        migrations.AddField(
            model_name='tbcheck',
            name='research_consent',
            field=models.BooleanField(null=True),
        ),
    ]
