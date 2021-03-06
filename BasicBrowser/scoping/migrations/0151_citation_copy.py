# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-10-20 12:07
from __future__ import unicode_literals

import django.contrib.postgres.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('scoping', '0150_auto_20171020_1206'),
    ]

    operations = [
        migrations.CreateModel(
            name='Citation_copy',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('au', models.TextField(null=True)),
                ('py', models.IntegerField(null=True)),
                ('so', models.TextField(null=True)),
                ('vl', models.IntegerField(null=True)),
                ('bp', models.IntegerField(null=True)),
                ('doi', models.TextField(db_index=True, null=True, unique=True)),
                ('ftext', models.TextField(db_index=True)),
                ('alt_text', django.contrib.postgres.fields.ArrayField(base_field=models.TextField(), null=True, size=None)),
                ('docmatches', models.IntegerField(null=True)),
                ('referent', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='scoping.Doc_2')),
            ],
        ),
    ]
