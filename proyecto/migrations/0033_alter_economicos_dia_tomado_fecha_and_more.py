# Generated by Django 4.2.9 on 2024-06-04 23:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proyecto', '0032_alter_catorcenas_fecha_final_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='economicos_dia_tomado',
            name='fecha',
            field=models.DateField(db_index=True, null=True),
        ),
        migrations.AlterField(
            model_name='tablafestivos',
            name='dia_festivo',
            field=models.DateField(db_index=True, null=True),
        ),
        migrations.AlterField(
            model_name='vacaciones_dias_tomados',
            name='fecha_fin',
            field=models.DateField(db_index=True, null=True),
        ),
        migrations.AlterField(
            model_name='vacaciones_dias_tomados',
            name='fecha_inicio',
            field=models.DateField(db_index=True, null=True),
        ),
    ]
