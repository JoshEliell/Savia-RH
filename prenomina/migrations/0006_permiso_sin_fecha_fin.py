# Generated by Django 4.2.9 on 2024-04-14 02:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('prenomina', '0005_permiso_goce_fecha_fin'),
    ]

    operations = [
        migrations.AddField(
            model_name='permiso_sin',
            name='fecha_fin',
            field=models.DateField(null=True),
        ),
    ]