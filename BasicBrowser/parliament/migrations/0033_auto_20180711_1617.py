# Generated by Django 2.0.5 on 2018-07-11 16:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('parliament', '0032_auto_20180711_1611'),
    ]

    operations = [
        migrations.RenameField(
            model_name='search',
            old_name='search_object',
            new_name='search_object_type',
        ),
    ]
