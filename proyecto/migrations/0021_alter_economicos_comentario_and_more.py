# Generated by Django 4.2.9 on 2024-04-04 23:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proyecto', '0020_alter_economicos_dia_tomado_comentario'),
    ]

    operations = [
        migrations.AlterField(
            model_name='economicos',
            name='comentario',
            field=models.TextField(null=True),
        ),
        migrations.AlterField(
            model_name='historicaleconomicos',
            name='comentario',
            field=models.TextField(null=True),
        ),
    ]