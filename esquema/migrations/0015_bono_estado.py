# Generated by Django 4.2.9 on 2024-08-02 19:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('esquema', '0014_solicitud_comentario'),
    ]

    operations = [
        migrations.AddField(
            model_name='bono',
            name='estado',
            field=models.BooleanField(default=False),
        ),
    ]
