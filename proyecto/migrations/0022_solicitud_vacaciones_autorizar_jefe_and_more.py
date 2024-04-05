# Generated by Django 4.2.9 on 2024-04-05 15:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('proyecto', '0021_alter_economicos_comentario_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='solicitud_vacaciones',
            name='autorizar_jefe',
            field=models.BooleanField(default=None, null=True),
        ),
        migrations.AddField(
            model_name='solicitud_vacaciones',
            name='perfil_gerente',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='perfil_vacacion_gerente', to='proyecto.perfil'),
        ),
    ]