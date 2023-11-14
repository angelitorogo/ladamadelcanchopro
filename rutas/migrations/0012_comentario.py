# Generated by Django 4.2.4 on 2023-11-06 14:54

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('rutas', '0011_alter_ruta_claves_alter_ruta_distancia_total'),
    ]

    operations = [
        migrations.CreateModel(
            name='Comentario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('texto', models.TextField(default='null')),
                ('fecha_created', models.DateTimeField(auto_now_add=True)),
                ('ruta', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rutas.ruta')),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'comentario',
                'verbose_name_plural': 'comentarios',
                'ordering': ['-fecha_created'],
            },
        ),
    ]
