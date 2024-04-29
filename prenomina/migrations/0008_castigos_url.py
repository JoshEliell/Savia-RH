# Generated by Django 4.2.9 on 2024-04-26 20:48

import django.core.validators
from django.db import migrations, models
import prenomina.models


class Migration(migrations.Migration):

    dependencies = [
        ('prenomina', '0007_castigos_fecha_fin'),
    ]

    operations = [
        migrations.AddField(
            model_name='castigos',
            name='url',
            field=models.FileField(default=None, unique=True, upload_to='prenomina/', validators=[prenomina.models.validar_size, django.core.validators.FileExtensionValidator(allowed_extensions=['pdf', 'png', 'jpg', 'jpeg'])]),
            preserve_default=False,
        ),
    ]
