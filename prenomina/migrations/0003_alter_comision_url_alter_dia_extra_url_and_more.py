# Generated by Django 4.2.7 on 2024-03-30 03:02

import django.core.validators
from django.db import migrations, models
import prenomina.models


class Migration(migrations.Migration):

    dependencies = [
        ('prenomina', '0002_comision_url_incapacidades_url_permiso_goce_url_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comision',
            name='url',
            field=models.FileField(unique=True, upload_to='prenomina/', validators=[prenomina.models.validar_size, django.core.validators.FileExtensionValidator(allowed_extensions=['pdf', 'png', 'jpg', 'jpeg'])]),
        ),
        migrations.AlterField(
            model_name='dia_extra',
            name='url',
            field=models.FileField(unique=True, upload_to='prenomina/', validators=[prenomina.models.validar_size, django.core.validators.FileExtensionValidator(allowed_extensions=['pdf', 'png', 'jpg', 'jpeg'])]),
        ),
        migrations.AlterField(
            model_name='incapacidades',
            name='url',
            field=models.FileField(unique=True, upload_to='prenomina/', validators=[prenomina.models.validar_size, django.core.validators.FileExtensionValidator(allowed_extensions=['pdf', 'png', 'jpg', 'jpeg'])]),
        ),
        migrations.AlterField(
            model_name='permiso_goce',
            name='url',
            field=models.FileField(unique=True, upload_to='prenomina/', validators=[prenomina.models.validar_size, django.core.validators.FileExtensionValidator(allowed_extensions=['pdf', 'png', 'jpg', 'jpeg'])]),
        ),
        migrations.AlterField(
            model_name='permiso_sin',
            name='url',
            field=models.FileField(unique=True, upload_to='prenomina/', validators=[prenomina.models.validar_size, django.core.validators.FileExtensionValidator(allowed_extensions=['pdf', 'png', 'jpg', 'jpeg'])]),
        ),
    ]
