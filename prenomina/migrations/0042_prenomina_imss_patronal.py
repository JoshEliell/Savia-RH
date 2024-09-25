# Generated by Django 4.2.9 on 2024-09-24 22:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('proyecto', '0054_datosisr_activo_datosisr_indicador'),
        ('prenomina', '0041_prenomina_fonacot_prenomina_indicador_isr_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='prenomina',
            name='imss_patronal',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='proyecto.variables_imss_patronal'),
        ),
    ]
