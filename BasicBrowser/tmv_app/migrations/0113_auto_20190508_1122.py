# Generated by Django 2.2 on 2019-05-08 11:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tmv_app', '0112_auto_20190508_0900'),
    ]

    operations = [
        migrations.AddField(
            model_name='runstats',
            name='beta',
            field=models.FloatField(default=None, help_text='Concentration parameter of Dirichlet distribution of words in topics.Low (high) values indicate that topics should be composed of few (many) words.Also called eta.', null=True),
        ),
        migrations.AlterField(
            model_name='runstats',
            name='alpha',
            field=models.FloatField(default=0.01, help_text='Concentration parameter of Dirichlet distribution of topics in documents(try higher values in LDA, including > 1). Low (high) values indicate thatdocuments should be composed of few (many) topics. Also called theta.', null=True),
        ),
    ]
