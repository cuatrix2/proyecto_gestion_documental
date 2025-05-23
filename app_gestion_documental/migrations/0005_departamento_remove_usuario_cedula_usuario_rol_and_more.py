# Generated by Django 5.2 on 2025-05-21 16:10

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_gestion_documental', '0004_remove_rol_id_rol_remove_usuario_id_usuario_rol_id_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Departamento',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre_departamento', models.CharField(max_length=100)),
                ('descripcion', models.TextField()),
            ],
        ),
        migrations.RemoveField(
            model_name='usuario',
            name='cedula',
        ),
        migrations.AddField(
            model_name='usuario',
            name='rol',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='usuarios', to='app_gestion_documental.rol'),
        ),
        migrations.AlterField(
            model_name='rol',
            name='nombre_rol',
            field=models.CharField(max_length=100),
        ),
        migrations.CreateModel(
            name='Carpeta',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100)),
                ('descripcion', models.TextField(blank=True)),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True)),
                ('usuario_creador', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='carpetas', to='app_gestion_documental.usuario')),
            ],
        ),
        migrations.AddField(
            model_name='rol',
            name='departamento',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='roles', to='app_gestion_documental.departamento'),
        ),
        migrations.AddField(
            model_name='usuario',
            name='departamento',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='usuarios', to='app_gestion_documental.departamento'),
        ),
        migrations.CreateModel(
            name='Documento',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre_archivo', models.CharField(max_length=255)),
                ('descripcion', models.TextField(blank=True)),
                ('tipo_archivo', models.CharField(max_length=50)),
                ('tamano', models.FloatField()),
                ('fecha_subida', models.DateTimeField(auto_now_add=True)),
                ('ruta_archivo', models.TextField()),
                ('texto_extraido', models.TextField(blank=True, null=True)),
                ('estado_ocr', models.CharField(blank=True, max_length=50, null=True)),
                ('carpeta', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='documentos', to='app_gestion_documental.carpeta')),
                ('usuario_subidor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='documentos', to='app_gestion_documental.usuario')),
            ],
        ),
        migrations.CreateModel(
            name='HistorialChat',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titulo', models.CharField(max_length=200)),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True)),
                ('carpeta', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='chats', to='app_gestion_documental.carpeta')),
                ('documento', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='chats', to='app_gestion_documental.documento')),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='historiales_chat', to='app_gestion_documental.usuario')),
            ],
        ),
        migrations.CreateModel(
            name='MensajeChat',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('contenido', models.TextField()),
                ('rol_mensaje', models.CharField(max_length=50)),
                ('fecha_envio', models.DateTimeField(auto_now_add=True)),
                ('chat', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='mensajes', to='app_gestion_documental.historialchat')),
            ],
        ),
        migrations.CreateModel(
            name='TransferenciaDocumento',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_transferencia', models.DateTimeField(auto_now_add=True)),
                ('departamento_destino', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transferencias_destino', to='app_gestion_documental.departamento')),
                ('departamento_origen', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transferencias_origen', to='app_gestion_documental.departamento')),
                ('documento', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transferencias', to='app_gestion_documental.documento')),
                ('usuario_responsable', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transferencias_realizadas', to='app_gestion_documental.usuario')),
            ],
        ),
    ]
