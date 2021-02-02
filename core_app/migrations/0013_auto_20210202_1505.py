# Generated by Django 3.1.4 on 2021-02-02 15:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core_app', '0012_calibration_detected_amplification'),
    ]

    operations = [
        migrations.RenameField(
            model_name='calibration',
            old_name='detected_amplification',
            new_name='amplification_test',
        ),
        migrations.AddField(
            model_name='calibration',
            name='amplification_information',
            field=models.TextField(null=True),
        ),
    ]
