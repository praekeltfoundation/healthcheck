# Generated by Django 3.1.14 on 2023-10-10 09:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userprofile', '0015_auto_20231004_1612'),
    ]

    operations = [
        migrations.AlterField(
            model_name='healthcheckuserprofile',
            name='province',
            field=models.CharField(blank=True, choices=[('ZA-EC', 'Eastern Cape'), ('ZA-FS', 'Free State'), ('ZA-GT', 'Gauteng'), ('ZA-LP', 'Limpopo'), ('ZA-MP', 'Mpumalanga'), ('ZA-NC', 'Northern Cape'), ('ZA-NL', 'Kwazulu-Natal'), ('ZA-NW', 'North-West (South Africa)'), ('ZA-WC', 'Western Cape')], default='', max_length=6, null=True),
        ),
    ]
