# Generated by Django 2.0.5 on 2018-06-11 11:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('scoping', '0204_docstatement_user'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='docownership',
            name='docstat',
        ),
    ]