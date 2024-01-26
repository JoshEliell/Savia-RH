# Generated by Django 4.1.1 on 2024-01-20 23:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proyecto', '0024_remove_variables_imss_patronal_riesgo_trabajo'),
    ]

    operations = [
        migrations.AddField(
            model_name='salariodatos',
            name='prima_vacacional',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='variables_imss_patronal',
            name='cf_obrero',
            field=models.DecimalField(decimal_places=4, default=0, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='variables_imss_patronal',
            name='cf_patron',
            field=models.DecimalField(decimal_places=4, default=0, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='variables_imss_patronal',
            name='cuota_fija',
            field=models.DecimalField(decimal_places=4, default=0, max_digits=10, null=True),
        ),
    ]