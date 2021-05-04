# Generated by Django 3.1.4 on 2021-05-04 15:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core_app', '0024_auto_20210504_1645'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sample',
            name='status',
            field=models.PositiveSmallIntegerField(choices=[(1, 'Pending'), (2, 'Classified'), (3, 'Txt file is incomplete'), (4, 'Dataframe is incomplete')], default=1),
        ),
    ]
