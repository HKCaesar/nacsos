# Generated by Django 2.2 on 2019-06-11 11:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('scoping', '0287_auto_20190605_1315'),
    ]

    operations = [
        migrations.RenameField(
            model_name='intervention',
            old_name='medium',
            new_name='medium2',
        ),
    ]