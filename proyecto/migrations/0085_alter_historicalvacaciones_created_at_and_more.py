# Generated by Django 4.1.1 on 2023-06-11 01:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proyecto', '0084_alter_status_fecha_planta'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historicalvacaciones',
            name='created_at',
            field=models.DateTimeField(null=True),
        ),
        migrations.AlterField(
            model_name='vacaciones',
            name='created_at',
            field=models.DateTimeField(null=True),
        ),
    ]
