from django.contrib import admin

# Register your models here.
from .models import Ruta, Imagen, Video, Comentario

# Register your models here.
class RutaAdmin(admin.ModelAdmin):
    list_display=('id','nombre', 'tiempo_total','distancia_total', 'desnivel_pos' ,'fecha_realizacion')
    
admin.site.register(Ruta, RutaAdmin)

class ImagenAdmin(admin.ModelAdmin):
    list_display=('ruta', 'imagen', 'fecha_created')
    
admin.site.register(Imagen, ImagenAdmin)


class VideoAdmin(admin.ModelAdmin):
    list_display=('ruta', 'video', 'fecha_created')
    
admin.site.register(Video, VideoAdmin)

class ComentarioAdmin(admin.ModelAdmin):
    list_display=('usuario', 'ruta', 'texto', 'fecha_created')
    
admin.site.register(Comentario, ComentarioAdmin)
