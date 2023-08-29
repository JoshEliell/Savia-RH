# Generated by Django 4.1.1 on 2023-08-28 15:45

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import simple_history.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('proyecto', '0009_historicalstatus_fecha_cedula_status_fecha_cedula'),
    ]

    operations = [
        migrations.CreateModel(
            name='HistoricalDatos_baja',
            fields=[
                ('id', models.BigIntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('fecha', models.DateField(null=True)),
                ('finiquito', models.DecimalField(decimal_places=2, default=0, max_digits=14, null=True)),
                ('liquidacion', models.DecimalField(decimal_places=2, default=0, max_digits=14, null=True)),
                ('motivo', models.CharField(max_length=50, null=True)),
                ('exitosa', models.BooleanField(default=None, null=True)),
                ('demanda', models.BooleanField(default=None, null=True)),
                ('created_at', models.DateTimeField(blank=True, editable=False)),
                ('updated_at', models.DateTimeField(blank=True, editable=False)),
                ('history_change_reason', models.TextField(null=True)),
                ('editado', models.CharField(blank=True, max_length=50)),
                ('complete', models.BooleanField(default=False)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('status', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='proyecto.status')),
            ],
            options={
                'verbose_name': 'historical datos_baja',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='Datos_baja',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha', models.DateField(null=True)),
                ('finiquito', models.DecimalField(decimal_places=2, default=0, max_digits=14, null=True)),
                ('liquidacion', models.DecimalField(decimal_places=2, default=0, max_digits=14, null=True)),
                ('motivo', models.CharField(max_length=50, null=True)),
                ('exitosa', models.BooleanField(default=None, null=True)),
                ('demanda', models.BooleanField(default=None, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('editado', models.CharField(blank=True, max_length=50)),
                ('complete', models.BooleanField(default=False)),
                ('status', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='proyecto.status')),
            ],
        ),
    ]
