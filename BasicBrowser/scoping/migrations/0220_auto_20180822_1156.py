# Generated by Django 2.0.5 on 2018-08-22 11:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scoping', '0219_auto_20180822_1140'),
    ]

    operations = [
        migrations.AddField(
            model_name='studyeffect',
            name='control_sample_size',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='studyeffect',
            name='geographic_location',
            field=models.TextField(null=True),
        ),
        migrations.AlterField(
            model_name='studyeffect',
            name='effect_direction',
            field=models.IntegerField(choices=[(1, 'Increase'), (-1, 'Decrease')]),
        ),
        migrations.AlterField(
            model_name='studyeffect',
            name='test_statistic',
            field=models.FloatField(blank=True, null=True),
        ),
    ]
