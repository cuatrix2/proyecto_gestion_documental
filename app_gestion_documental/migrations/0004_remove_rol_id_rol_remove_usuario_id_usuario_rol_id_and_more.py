# Generated by Django 5.2 on 2025-05-21 02:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_gestion_documental', '0003_rol'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='rol',
            name='id_rol',
        ),
        migrations.RemoveField(
            model_name='usuario',
            name='id_usuario',
        ),
        migrations.AddField(
            model_name='rol',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AddField(
            model_name='usuario',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]
