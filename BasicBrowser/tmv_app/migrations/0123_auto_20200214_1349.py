# Generated by Django 2.2.9 on 2020-02-14 13:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('parliament', '0055_auto_20200206_0942'),
        ('scoping', '0315_auto_20200114_1420'),
        ('tmv_app', '0122_auto_20200211_1731'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='DocTopic',
            new_name='DocTopicArchive',
        ),
        migrations.DeleteModel(
            name='DocTopicCopy',
        ),
    ]