# Generated by Django 2.0.5 on 2018-09-13 16:44

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('twitter', '0002_auto_20180913_1643'),
    ]

    operations = [
        migrations.AlterField(
            model_name='twitterbasemodel',
            name='created_at',
            field=models.DateTimeField(null=True),
        ),
        migrations.AlterField(
            model_name='twitterbasemodel',
            name='entities',
            field=django.contrib.postgres.fields.jsonb.JSONField(null=True),
        ),
        migrations.AlterField(
            model_name='twitterbasemodel',
            name='lang',
            field=models.CharField(max_length=10, null=True),
        ),
    ]