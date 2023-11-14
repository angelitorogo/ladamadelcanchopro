from django.urls import path
from .views import mapa_page, rutas_page, upload_page, cargar_track, ruta_page, editarRuta_page,eliminarRuta_page, home_page, visualizarRuta, guardarClaves

urlpatterns = [
    path('', home_page, name="home"),
    path('rutas', rutas_page, name="rutas"),
    path('ruta/<int:ruta_id>', ruta_page, name="ruta"),
    path('editar-ruta/<int:ruta_id>', editarRuta_page, name="editar-ruta"),
    path('mapa', mapa_page, name="mapa"),
    path('upload', upload_page, name="upload"),
    path('cargar-track/<filename>', cargar_track, name = "cargar-track"),
    path('eliminar-ruta/<int:ruta_id>', eliminarRuta_page, name="eliminar-ruta"),
    path('visualizar-ruta', visualizarRuta, name="visualizar-ruta"),
    path('guardar-claves', guardarClaves, name="guardar-claves"),
    
]
