# Generated by Django 3.2.3 on 2022-09-27 01:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proyecto', '0008_auto_20220926_2047'),
    ]

    operations = [
        migrations.AlterField(
            model_name='datosbancarios',
            name='numero_de_tarjeta',
            field=models.CharField(blank=True, max_length=18, null=True),
        ),
    ]