# Generated by Django 4.1.1 on 2023-01-11 23:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('proyecto', '0032_remove_regimen_domingo_remove_regimen_jueves_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='status',
            name='regimen',
        ),
        migrations.DeleteModel(
            name='Regimen',
        ),
    ]