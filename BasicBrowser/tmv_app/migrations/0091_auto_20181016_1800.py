# Generated by Django 2.0.5 on 2018-10-16 18:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tmv_app', '0090_docdynamictopic'),
    ]

    operations = [
        migrations.AlterField(
            model_name='runstats',
            name='method',
            field=models.CharField(choices=[('LD', 'lda'), ('HL', 'hlda'), ('DT', 'dtm'), ('NM', 'nmf'), ('BD', 'BleiDTM')], default='NM', max_length=2),
        ),
    ]
