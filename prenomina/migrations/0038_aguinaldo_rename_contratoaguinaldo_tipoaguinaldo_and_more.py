# Generated by Django 4.2.7 on 2024-06-20 18:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('proyecto', '0039_tablasubsidio'),
        ('prenomina', '0037_contratoaguinaldo_aguinaldoprenomina'),
    ]

    operations = [
        migrations.CreateModel(
            name='Aguinaldo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha', models.DateField(null=True)),
                ('monto', models.DecimalField(decimal_places=2, default=0, max_digits=14, null=True)),
                ('mes', models.IntegerField(default=None, null=True)),
                ('complete', models.BooleanField(default=False)),
                ('catorcena', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='proyecto.catorcenas')),
                ('empleado', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='proyecto.costo')),
            ],
        ),
        migrations.RenameModel(
            old_name='ContratoAguinaldo',
            new_name='TipoAguinaldo',
        ),
        migrations.DeleteModel(
            name='AguinaldoPrenomina',
        ),
        migrations.AddField(
            model_name='aguinaldo',
            name='tipo',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='prenomina.tipoaguinaldo'),
        ),
    ]
