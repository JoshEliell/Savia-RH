# Generated by Django 4.2.9 on 2024-08-05 18:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('esquema', '0015_bono_estado'),
    ]

    operations = [
        migrations.AlterField(
            model_name='solicitud',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]
