# Generated by Django 4.1.1 on 2022-12-14 23:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('proyecto', '0029_status_regimen'),
    ]

    operations = [
        migrations.CreateModel(
            name='TablaFestivos',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_nacimiento', models.DateField(null=True)),
                ('complete', models.BooleanField(default=False)),
            ],
        ),
        migrations.AlterField(
            model_name='status',
            name='regimen',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='proyecto.regimen'),
        ),
    ]