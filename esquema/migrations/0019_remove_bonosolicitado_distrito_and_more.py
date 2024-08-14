# Generated by Django 4.2.9 on 2024-08-07 19:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('esquema', '0018_alter_bonosolicitado_puesto'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='bonosolicitado',
            name='distrito',
        ),
        migrations.RemoveField(
            model_name='bonosolicitado',
            name='puesto',
        ),
        migrations.AddField(
            model_name='bonosolicitado',
            name='bono',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='esquema.bono'),
        ),
    ]