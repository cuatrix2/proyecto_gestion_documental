# Generated by Django 5.2 on 2025-05-21 02:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_gestion_documental', '0002_usuario_cedula'),
    ]

    operations = [
        migrations.CreateModel(
            name='Rol',
            fields=[
                ('id_rol', models.AutoField(primary_key=True, serialize=False)),
                ('nombre_rol', models.CharField(max_length=50)),
                ('descripcion', models.TextField()),
            ],
        ),
    ]
