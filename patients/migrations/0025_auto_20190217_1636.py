# Generated by Django 2.1.5 on 2019-02-17 15:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('patients', '0024_bmd'),
    ]

    operations = [
        migrations.AddField(
            model_name='analysis',
            name='patient',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='patients.Patient', verbose_name='paziente'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='bmd',
            name='patient',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='patients.Patient', verbose_name='paziente'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='bmd',
            name='fn_bmd',
            field=models.FloatField(blank=True, null=True, verbose_name='femoral neck BMD'),
        ),
        migrations.AlterField(
            model_name='bmd',
            name='fn_t',
            field=models.FloatField(blank=True, null=True, verbose_name='femoral neck T-score'),
        ),
        migrations.AlterField(
            model_name='bmd',
            name='fn_z',
            field=models.FloatField(blank=True, null=True, verbose_name='femoral neck Z-score'),
        ),
        migrations.AlterField(
            model_name='bmd',
            name='ft_bmd',
            field=models.FloatField(blank=True, null=True, verbose_name='femorale totale BMD'),
        ),
        migrations.AlterField(
            model_name='bmd',
            name='ft_t',
            field=models.FloatField(blank=True, null=True, verbose_name='femorale totale T-score'),
        ),
        migrations.AlterField(
            model_name='bmd',
            name='ft_z',
            field=models.FloatField(blank=True, null=True, verbose_name='femorale totale Z-score'),
        ),
        migrations.AlterField(
            model_name='bmd',
            name='ls_bmd',
            field=models.FloatField(blank=True, null=True, verbose_name='lombosacrale BMD'),
        ),
        migrations.AlterField(
            model_name='bmd',
            name='ls_t',
            field=models.FloatField(blank=True, null=True, verbose_name='lombosacrale T-score'),
        ),
        migrations.AlterField(
            model_name='bmd',
            name='ls_z',
            field=models.FloatField(blank=True, null=True, verbose_name='lombosacrale Z-score'),
        ),
    ]
