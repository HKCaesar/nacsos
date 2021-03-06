# Generated by Django 2.0.5 on 2018-05-25 13:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('scoping', '0193_tag_document_linked'),
    ]

    operations = [
        migrations.AddField(
            model_name='docpar',
            name='technology',
            field=models.ManyToManyField(db_index=True, to='scoping.Technology'),
        ),
        migrations.AddField(
            model_name='note',
            name='par',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='scoping.DocPar'),
        ),
        migrations.AddField(
            model_name='technology',
            name='level',
            field=models.IntegerField(default=1),
        ),
        migrations.AlterField(
            model_name='note',
            name='doc',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='scoping.Doc'),
        ),
    ]
