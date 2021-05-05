# Generated by Django 3.1.4 on 2021-05-05 11:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core_app', '0025_auto_20210504_1702'),
    ]

    operations = [
        migrations.RenameField(
            model_name='sample',
            old_name='dataframe_complete',
            new_name='all_cpg',
        ),
        migrations.AddField(
            model_name='sample',
            name='amplification_fit',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='sample',
            name='missing_cpg',
            field=models.CharField(default='', max_length=25, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='sample',
            name='status',
            field=models.PositiveSmallIntegerField(choices=[(0, 'Pending'), (1111, 'Classified'), (1, 'Txt file is incomplete'), (2, 'Some CpGs are missing'), (3, 'Insufficient amplification')], default=0),
        ),
    ]
