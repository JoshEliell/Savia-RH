# Generated by Django 4.1.1 on 2022-12-08 22:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('proyecto', '0019_userdatos_admin'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userdatos',
            name='admin',
        ),
    ]