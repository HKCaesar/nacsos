# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-10-11 13:38
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scoping', '0132_project_role'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='queries',
            field=models.IntegerField(default=0),
        ),
    ]
