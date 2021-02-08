# Generated by Django 2.2.2 on 2021-01-26 21:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scoping', '0336_docusercat_countries'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='number_entry',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='docusercat',
            name='number',
            field=models.IntegerField(null=True),
        ),
    ]