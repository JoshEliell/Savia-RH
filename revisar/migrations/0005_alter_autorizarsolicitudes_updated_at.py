# Generated by Django 4.2.9 on 2024-09-04 18:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('revisar', '0004_autorizarprenomina'),
    ]

    operations = [
        migrations.AlterField(
            model_name='autorizarsolicitudes',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, db_index=True),
        ),
    ]