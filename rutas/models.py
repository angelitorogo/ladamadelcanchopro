from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Ruta(models.Model):
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField(default='null')
    fecha_realizacion = models.DateField()
    fecha_subida = models.DateTimeField(auto_now_add=True)
    claves = models.CharField(default='null',max_length=400)
    trak = models.FileField(upload_to='tracks/')  # Guarda los archivos GPX en una carpeta 'tracks/'
    inicio = models.CharField(max_length=150, default='null')
    distancia_total = models.FloatField(default=0)
    desnivel_pos = models.IntegerField(default=0)
    desnivel_neg = models.IntegerField(default=0)
    tiempo_total = models.CharField(max_length=150, default='null')
    alt_max = models.IntegerField(default=0)
    alt_min = models.IntegerField(default=0)
    puntos = models.TextField(default='null')
    altitudes = models.TextField(default='null')
    distancias = models.TextField(default='null')
    

    class Meta:
        verbose_name = 'ruta'
        verbose_name_plural = 'rutas'
        ordering = ['-fecha_realizacion']
        
    def __str__(self):
        return self.nombre
        
class Imagen(models.Model):
    ruta = models.ForeignKey(Ruta, on_delete=models.CASCADE)
    imagen = models.ImageField(upload_to='images/')
    fecha_created = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'imagen'
        verbose_name_plural = 'imagenes'
        ordering = ['-fecha_created']

        
class Video(models.Model):
    ruta = models.ForeignKey(Ruta, on_delete=models.CASCADE)
    video = models.FileField(upload_to='videos/')
    fecha_created = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'video'
        verbose_name_plural = 'videos'
        ordering = ['-fecha_created']
        
        

class Comentario(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    ruta = models.ForeignKey(Ruta, on_delete=models.CASCADE)
    texto = models.TextField(default='null')
    fecha_created = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'comentario'
        verbose_name_plural = 'comentarios'
        ordering = ['fecha_created']