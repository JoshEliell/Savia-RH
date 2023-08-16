# Generated by Django 4.1.1 on 2023-08-10 19:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proyecto', '0007_alter_historicalbonos_options_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='solicitud_vacaciones',
            name='asunto',
        ),
        migrations.AddField(
            model_name='solicitud_vacaciones',
            name='asunto',
            field=models.ManyToManyField(blank=True, to='proyecto.trabajos_encomendados'),
        ),
    ]
