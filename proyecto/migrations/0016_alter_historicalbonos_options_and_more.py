# Generated by Django 4.2.7 on 2024-03-18 18:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proyecto', '0015_costoanterior'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='historicalbonos',
            options={'get_latest_by': 'history_date', 'ordering': ('-history_date', '-history_id'), 'verbose_name': 'historical bonos'},
        ),
        migrations.AlterModelOptions(
            name='historicalcosto',
            options={'get_latest_by': 'history_date', 'ordering': ('-history_date', '-history_id'), 'verbose_name': 'historical costo'},
        ),
        migrations.AlterModelOptions(
            name='historicaldatos_baja',
            options={'get_latest_by': 'history_date', 'ordering': ('-history_date', '-history_id'), 'verbose_name': 'historical datos_baja'},
        ),
        migrations.AlterModelOptions(
            name='historicaldatosbancarios',
            options={'get_latest_by': 'history_date', 'ordering': ('-history_date', '-history_id'), 'verbose_name': 'historical datos bancarios'},
        ),
        migrations.AlterModelOptions(
            name='historicaleconomicos',
            options={'get_latest_by': 'history_date', 'ordering': ('-history_date', '-history_id'), 'verbose_name': 'historical economicos'},
        ),
        migrations.AlterModelOptions(
            name='historicalempleado_cv',
            options={'get_latest_by': 'history_date', 'ordering': ('-history_date', '-history_id'), 'verbose_name': 'historical empleado_cv'},
        ),
        migrations.AlterModelOptions(
            name='historicalperfil',
            options={'get_latest_by': 'history_date', 'ordering': ('-history_date', '-history_id'), 'verbose_name': 'historical perfil'},
        ),
        migrations.AlterModelOptions(
            name='historicalregistropatronal',
            options={'get_latest_by': 'history_date', 'ordering': ('-history_date', '-history_id'), 'verbose_name': 'historical registro patronal'},
        ),
        migrations.AlterModelOptions(
            name='historicalstatus',
            options={'get_latest_by': 'history_date', 'ordering': ('-history_date', '-history_id'), 'verbose_name': 'historical status'},
        ),
        migrations.AlterModelOptions(
            name='historicaluniformes',
            options={'get_latest_by': 'history_date', 'ordering': ('-history_date', '-history_id'), 'verbose_name': 'historical uniformes'},
        ),
        migrations.AlterModelOptions(
            name='historicalvacaciones',
            options={'get_latest_by': 'history_date', 'ordering': ('-history_date', '-history_id'), 'verbose_name': 'historical vacaciones'},
        ),
        migrations.AlterField(
            model_name='historicalbonos',
            name='history_date',
            field=models.DateTimeField(),
        ),
        migrations.AlterField(
            model_name='historicalcosto',
            name='history_date',
            field=models.DateTimeField(),
        ),
        migrations.AlterField(
            model_name='historicaldatos_baja',
            name='history_date',
            field=models.DateTimeField(),
        ),
        migrations.AlterField(
            model_name='historicaldatosbancarios',
            name='history_date',
            field=models.DateTimeField(),
        ),
        migrations.AlterField(
            model_name='historicaleconomicos',
            name='history_date',
            field=models.DateTimeField(),
        ),
        migrations.AlterField(
            model_name='historicalempleado_cv',
            name='history_date',
            field=models.DateTimeField(),
        ),
        migrations.AlterField(
            model_name='historicalperfil',
            name='history_date',
            field=models.DateTimeField(),
        ),
        migrations.AlterField(
            model_name='historicalregistropatronal',
            name='history_date',
            field=models.DateTimeField(),
        ),
        migrations.AlterField(
            model_name='historicalstatus',
            name='history_date',
            field=models.DateTimeField(),
        ),
        migrations.AlterField(
            model_name='historicaluniformes',
            name='history_date',
            field=models.DateTimeField(),
        ),
        migrations.AlterField(
            model_name='historicalvacaciones',
            name='history_date',
            field=models.DateTimeField(),
        ),
    ]
