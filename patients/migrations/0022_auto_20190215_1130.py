# Generated by Django 2.1.5 on 2019-02-15 10:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('patients', '0021_analysisname'),
    ]

    operations = [
        migrations.AlterField(
            model_name='analysisname',
            name='short_name',
            field=models.CharField(default='nn', max_length=25, verbose_name='abbreviazione'),
            preserve_default=False,
        ),
    ]