# Generated by Django 2.1.2 on 2019-02-05 15:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('parliament', '0044_merge_20181026_1551'),
        ('scoping', '0257_wosarticle_ems'),
    ]

    operations = [
        migrations.AddField(
            model_name='docownership',
            name='utterance',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='parliament.Utterance'),
        ),
        migrations.AddField(
            model_name='docownership',
            name='utterance_linked',
            field=models.BooleanField(default=True),
        ),
    ]
