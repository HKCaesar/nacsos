# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-11-07 10:12
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tmv_app', '0050_auto_20171106_1531'),
    ]

    operations = [
        migrations.AddField(
            model_name='topicarscores',
            name='share',
            field=models.FloatField(null=True),
        ),
    ]
