# Generated by Django 4.2.9 on 2024-08-01 15:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('esquema', '0013_alter_bono_importe'),
    ]

    operations = [
        migrations.AddField(
            model_name='solicitud',
            name='comentario',
            field=models.CharField(max_length=255, null=True),
        ),
    ]