# Generated by Django 4.1.1 on 2023-05-06 18:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('proyecto', '0069_alter_historicalbonos_options_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Solicitud_vacaciones',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('periodo', models.CharField(max_length=50, null=True)),
                ('fecha_inicio', models.DateField(null=True)),
                ('fecha_fin', models.DateField(null=True)),
                ('comentario', models.CharField(max_length=50, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('complete', models.BooleanField(default=False)),
                ('dia_inhabil', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='proyecto.dia_vacacion')),
                ('status', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='proyecto.status')),
            ],
        ),
        migrations.CreateModel(
            name='Solicitud_economicos',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('periodo', models.CharField(max_length=50, null=True)),
                ('fecha', models.DateField(null=True)),
                ('comentario', models.CharField(max_length=50, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('complete', models.BooleanField(default=False)),
                ('status', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='proyecto.status')),
            ],
        ),
    ]