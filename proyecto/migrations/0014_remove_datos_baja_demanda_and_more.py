# Generated by Django 4.1.1 on 2023-09-13 00:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('proyecto', '0013_historicalempleado_cv_empleado_cv'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='datos_baja',
            name='demanda',
        ),
        migrations.RemoveField(
            model_name='historicaldatos_baja',
            name='demanda',
        ),
    ]