# Generated by Django 4.1.1 on 2023-06-15 16:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proyecto', '0087_alter_datosbancarios_clabe_interbancaria_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='perfil',
            name='baja',
            field=models.BooleanField(default=False),
        ),
    ]
