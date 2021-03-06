# Generated by Django 2.2 on 2020-02-14 12:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('scoping', '0315_auto_20200114_1420'),
        ('twitter', '0020_auto_20200115_1237'),
    ]

    operations = [
        migrations.AddField(
            model_name='twittersearch',
            name='project_list',
            field=models.ManyToManyField(related_name='plist_TwitterSearches', to='scoping.Project'),
        ),
        migrations.AlterField(
            model_name='twittersearch',
            name='project',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='TwitterSearches', to='scoping.Project'),
        ),
    ]
