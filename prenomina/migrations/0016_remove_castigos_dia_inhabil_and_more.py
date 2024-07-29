# Generated by Django 4.2.9 on 2024-05-28 16:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('prenomina', '0015_descanso_prenomina_d_fecha_b837a0_idx_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='castigos',
            name='dia_inhabil',
        ),
        migrations.RemoveField(
            model_name='castigos',
            name='prenomina',
        ),
        migrations.RemoveField(
            model_name='comision',
            name='prenomina',
        ),
        migrations.RemoveField(
            model_name='descanso',
            name='prenomina',
        ),
        migrations.RemoveField(
            model_name='dia_extra',
            name='prenomina',
        ),
        migrations.RemoveField(
            model_name='domingo',
            name='prenomina',
        ),
        migrations.RemoveField(
            model_name='faltas',
            name='prenomina',
        ),
        migrations.RemoveField(
            model_name='incapacidades',
            name='dia_inhabil',
        ),
        migrations.RemoveField(
            model_name='incapacidades',
            name='prenomina',
        ),
        migrations.RemoveField(
            model_name='incapacidades',
            name='tipo',
        ),
        migrations.RemoveField(
            model_name='permiso_goce',
            name='dia_inhabil',
        ),
        migrations.RemoveField(
            model_name='permiso_goce',
            name='prenomina',
        ),
        migrations.RemoveField(
            model_name='permiso_sin',
            name='dia_inhabil',
        ),
        migrations.RemoveField(
            model_name='permiso_sin',
            name='prenomina',
        ),
        migrations.RemoveField(
            model_name='retardos',
            name='prenomina',
        ),
        migrations.DeleteModel(
            name='Aguinaldo_Contrato',
        ),
        migrations.DeleteModel(
            name='Castigos',
        ),
        migrations.DeleteModel(
            name='Comision',
        ),
        migrations.DeleteModel(
            name='Descanso',
        ),
        migrations.DeleteModel(
            name='Dia_extra',
        ),
        migrations.DeleteModel(
            name='Domingo',
        ),
        migrations.DeleteModel(
            name='Faltas',
        ),
        migrations.DeleteModel(
            name='Incapacidades',
        ),
        migrations.DeleteModel(
            name='Permiso_goce',
        ),
        migrations.DeleteModel(
            name='Permiso_sin',
        ),
        migrations.DeleteModel(
            name='Retardos',
        ),
        migrations.DeleteModel(
            name='Tipo_incapacidad',
        ),
    ]
