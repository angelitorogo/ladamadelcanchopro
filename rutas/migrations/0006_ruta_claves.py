# Generated by Django 4.2.4 on 2023-09-28 18:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rutas', '0005_remove_imagen_lat_remove_imagen_lng'),
    ]

    operations = [
        migrations.AddField(
            model_name='ruta',
            name='claves',
            field=models.CharField(default='null', max_length=255),
        ),
    ]
