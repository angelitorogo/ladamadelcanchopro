from django.shortcuts import render, redirect, reverse
from django.core import serializers
from django.contrib.auth.decorators import user_passes_test
from .models import Ruta, Imagen, Video, Comentario
from django.views.decorators.http import require_GET
from django.http import HttpResponse, JsonResponse
import os
import gpxpy
from django.conf import settings
from geopy.distance import geodesic
import cv2
import numpy as np
from moviepy.editor import VideoFileClip
import json
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import xml.etree.ElementTree as ET
from datetime import datetime
import requests
import math
from django.db.models import Q
from math import radians, sin, cos, sqrt, atan2
import wikipedia

# Create your views here.
def home_page(request):
    return render(request, 'rutas/home.html', {'title': 'Leyenda'})

def rutas_page(request): 
           
    tipo = ''
        
    if request.META.get('CONTENT_TYPE') == 'application/json':
                        
        data = json.loads(request.body)
        # Acceder a los valores
        tipo = data.get('tipo')
        busqueda = data.get('termino')
        
    else:
    
        busqueda = request.GET.get('termino', '')
        tipo = request.GET.get('tipo', '-fecha_realizacion')
    
    termino = ''
    distanciaTotal = 0
    desnivelTotal = 0
        
    # Obtiene el número de página
    pagina = int(request.GET.get('pag', 0))  # Si no se proporciona, asume la página 1

    # Define cuántos resultados quieres por página
    resultados_por_pagina = 12
    
    if request.method == 'POST':
        pagina = 0

    # Calcula el índice de inicio y fin para la consulta
    inicio = (pagina) * resultados_por_pagina
    fin = inicio + resultados_por_pagina

    # Realiza la consulta con prefetch_related y el slicing
    
    
    if request.method == 'POST' or busqueda != '':
        
        if busqueda != '':  # and pagina != 0
            termino = busqueda
        else:
            termino = request.POST.get('termino', '')
            
        
        rutas_con_imagenes = Ruta.objects.prefetch_related('imagen_set').filter(
            Q(nombre__icontains=termino) | 
            Q(descripcion__icontains=termino) |
            Q(claves__icontains=termino)
        ).order_by(tipo)[inicio:fin]
        total_rutas_con_imagenes = Ruta.objects.prefetch_related('imagen_set').filter(
            Q(nombre__icontains=termino) | 
            Q(descripcion__icontains=termino) |
            Q(claves__icontains=termino)
        ).order_by(tipo)
    
    else:
        
        rutas_con_imagenes = Ruta.objects.prefetch_related('imagen_set').all().order_by(tipo)[inicio:fin]
        total_rutas_con_imagenes = Ruta.objects.prefetch_related('imagen_set').order_by(tipo).all()

    rutas_con_coordenadas = []
    totalPaginas = math.ceil(len(total_rutas_con_imagenes) / resultados_por_pagina)
    
    for ruta in rutas_con_imagenes:

        rutas_con_coordenadas.append({
            'ruta': ruta,
            'coordenadas': ruta.puntos,
            'longitud':ruta.distancia_total,
            'desnivel': ruta.desnivel_pos
        })
        
    num_rutas = len(total_rutas_con_imagenes)
    
    for ruta in total_rutas_con_imagenes:
        distanciaTotal = distanciaTotal + ruta.distancia_total 
        desnivelTotal = desnivelTotal + ruta.desnivel_pos
    
    distanciaTotal = round(distanciaTotal, 2)

    if totalPaginas != 0:
        
        if request.META.get('CONTENT_TYPE') == 'application/json':
                        
            rutas_serializadas = []
            for ruta in rutas_con_imagenes:
                rutas_serializadas.append({
                'id': ruta.id,    
                'nombre': ruta.nombre,
                'descripcion': ruta.descripcion,
                'fecha_realizacion': ruta.fecha_realizacion.strftime('%Y-%m-%d'),  # Formatear la fecha
                'fecha_subida': ruta.fecha_subida.strftime('%Y-%m-%d %H:%M:%S'),  # Formatear la fecha y hora
                'claves': ruta.claves,
                'trak': ruta.trak.url,  # Obtener la URL del archivo trak
                'inicio': ruta.inicio,
                'distancia_total': ruta.distancia_total,
                'desnivel_pos': ruta.desnivel_pos,
                'desnivel_neg': ruta.desnivel_neg,
                'tiempo_total': ruta.tiempo_total,
                'alt_max': ruta.alt_max,
                'alt_min': ruta.alt_min,
                'puntos': ruta.puntos,
                'altitudes': ruta.altitudes,
                'distancias': ruta.distancias
            })
                
            return JsonResponse({
                'title': 'Rutas de senderismo',
                'rutas': rutas_serializadas,
                'totalPaginas': totalPaginas,
                'pagina': pagina + 1,
                'num_rutas': num_rutas,
                'termino': termino,
                'distanciaTotal': distanciaTotal,
                'desnivelTotal': desnivelTotal,
                'tipo': tipo
        })
             
        else:
            
            return render(request, 'rutas/rutas.html', {'title': 'Rutas de senderismo',
                                                    'rutas': rutas_con_coordenadas,
                                                    'totalPaginas': totalPaginas,
                                                    'pagina': pagina + 1,
                                                    'num_rutas': num_rutas,
                                                    'termino': termino,
                                                    'distanciaTotal': distanciaTotal,
                                                    'desnivelTotal': desnivelTotal,
                                                    'tipo': tipo})
    
    else:
        
        return render(request, 'rutas/rutas.html', {'title': 'Rutas de senderismo', 
                                                    'totalPaginas': totalPaginas, 
                                                    'termino': termino,
                                                    'tipo': tipo})
              
def mapa_page(request): 
    
    busqueda = False
    
    if request.method == 'POST':
        termino = request.POST.get('termino', '')
        busqueda = True
        rutas_con_imagenes = Ruta.objects.prefetch_related('imagen_set').filter(
            Q(nombre__icontains=termino) | 
            Q(descripcion__icontains=termino) |
            Q(claves__icontains=termino)
        )
        
    else:
        rutas_con_imagenes = Ruta.objects.prefetch_related('imagen_set').all()
        
    rutas_con_coordenadas = []
    
    # cargar normal en GET
    for ruta in rutas_con_imagenes:
        
        rutas_con_coordenadas.append({
                'ruta': ruta,
                'id':ruta.id,
        })
    
    num_rutas = len(rutas_con_coordenadas)
    
    rutas_json = rutas_con_coordenadas
    
    
    
    for ruta in rutas_json:
        ruta['id'] = ruta['ruta'].id
        ruta['inicio'] = ruta['ruta'].inicio
        ruta['puntos'] = ruta['ruta'].puntos
        ruta['distancia'] = ruta['ruta'].distancia_total
        ruta['desnivel'] = ruta['ruta'].desnivel_pos
        ruta['ruta'] = ruta['ruta'].nombre

        
    # Convierte rutas_con_coordenadas a formato JSON
    rutas_json = json.dumps(rutas_json)
    
    return render(request, 'rutas/mapa.html', {'title': 'Mapa',
                                               'rutas': rutas_con_coordenadas,
                                               'num_rutas':num_rutas,
                                               'rutas_json':rutas_json,
                                               'busqueda':busqueda})

@user_passes_test(lambda u: u.is_authenticated)
def upload_page(request): 
    
    ok = True
    algunoNo = False
    
    if request.method == 'POST':
        
        tracks = request.FILES.getlist('track')
        current_path = os.path.join(settings.DIR_MEDIA, 'tracks')
        
        
        for track in tracks:
            archivo_nombre = track.name.replace(' ', '-')
            extension = archivo_nombre.split('.')[-1]

            if archivo_nombre not in os.listdir(current_path) and extension == 'gpx':
                
                ok = subirTrack(track)
                
                if ok == False:
                    algunoNo = True
        
        if algunoNo == True:
            
            redirect_url = '/upload?uploadedButNotAll'
            return redirect(redirect_url)  
        
        else:
            
            redirect_url = '/upload?uploaded'
            return redirect(redirect_url)  
            
        
                
        
    return render(request, 'rutas/upload.html', {'title': 'Nueva Ruta'})

@user_passes_test(lambda u: u.is_authenticated)
def ruta_page(request, ruta_id):

    try:  
        
        ruta = Ruta.objects.get(id=ruta_id) 
        
        clavesStringTemp = ruta.claves.replace(":", "")
        clavesString = clavesStringTemp[:-1]
        
        lista_elementos = clavesString.split(',')
        lugares_a_buscar = tuple(lista_elementos)
 

        if request.method == 'POST':
        
            imagenes = request.FILES.getlist('imagen')
            videos = request.FILES.getlist('video')
            
            if len(imagenes) != 0 and len(videos) != 0:

                subirImagenesOVideos(ruta, imagenes, videos)
                
                redirect_url = '/ruta/{}?uploaded'.format(ruta_id)
                return redirect(redirect_url) 
            
            else:
                
                texto = request.POST.get('comment')
                
                comentario = Comentario()
        
                comentario.usuario = request.user
                comentario.ruta = ruta
                comentario.texto = texto
                
                comentario.save()
                        
                        
                
                redirect_url = '/ruta/{}?comment'.format(ruta_id)
                return redirect(redirect_url)
                
        imagenes = Imagen.objects.filter(ruta=ruta)
        imagenes_serializable = list(imagenes.values('id', 'ruta_id', 'imagen'))
        
        videos = Video.objects.filter(ruta=ruta)
        videos_serializable = list(videos.values('id', 'ruta_id', 'video'))
        
        comentarios = Comentario.objects.filter(ruta=ruta)
        
        comentarios_no_json = []
        
        for comentario in comentarios:
            comentario.fecha_created = comentario.fecha_created.strftime('%d-%m-%Y')
            comentarios_no_json.append({
                    'ruta': comentario.ruta.nombre,
                    'usuario':comentario.usuario.username,
                    'texto': comentario.texto,
                    'feha_created': comentario.fecha_created
            })
        
        comentarios_json = json.dumps(comentarios_no_json) 
        
        #Obtener primer punto para saber en que municipio nos encontramos en este track
        primer_punto = ruta.inicio
        
        #convertir primer punto que es string tipo (40.4242, -3,4545) en una tupla
        tupla_coordenadas = eval(primer_punto)
        
        #obtener codigo postal cercano a ese punto
        municipios = obtener_localidades(tupla_coordenadas[0], tupla_coordenadas[1])
            
        #Este bloque es para conseguir el codigo INE de un archivo de la AEMET en local
        ruta_json = os.path.join(settings.DIR_MEDIA, 'json', 'aemet.json')      
        # Abre el archivo JSON
        with open(ruta_json, 'r', encoding='utf-8') as archivo:
            # Carga el contenido del archivo JSON
            data = json.load(archivo)
            
            for municipio in municipios:

                # Define el string que quieres buscar
                string_busqueda = municipio

                # Itera sobre los registros y verifica si hay una coincidencia con el municipio antes conseguido
                codigoINE = None
                
                seguir = 0
                
                for registro in data:
                    if string_busqueda in registro.values():

                        codigoINE = registro['id'].replace('id', '')
                        
                        seguir = 1
                        
                    
                if seguir == 1:
                    municipioMeteo = string_busqueda
                    break    
                else:
                    municipioMeteo = municipio  
                    
            #El Tiempo
            tiempo = elTiempo(codigoINE)
            
            rutas_con_imagenes = Ruta.objects.prefetch_related('imagen_set').all()
            
            rutas_con_coordenadas = []
            
            # cargar normal en GET
            for ruta2 in rutas_con_imagenes:
                
                rutas_con_coordenadas.append({
                        'ruta': ruta2,
                        'id':ruta2.id,
                })
                    

            for ruta2 in rutas_con_coordenadas:
                ruta2['id'] = ruta2['ruta'].id
                ruta2['inicio'] = ruta2['ruta'].inicio
                ruta2['puntos'] = ruta2['ruta'].puntos
                ruta2['distancia'] = ruta2['ruta'].distancia_total
                ruta2['desnivel'] = ruta2['ruta'].desnivel_pos
                ruta2['ruta'] = ruta2['ruta'].nombre
                ruta2['cercania'] = 0

            
            # Eliminamos los paréntesis y separamos las coordenadas
            coordenadas_lista = ruta.inicio.strip('()').split(', ')
            latitud, longitud = map(float, coordenadas_lista)

            # Creamos el diccionario
            coordenadas_inicio = {'lat': latitud, 'lng': longitud}
                    
            #Saber rutas cercanas
            for ruta3 in rutas_con_coordenadas:
                coordenadas1 = coordenadas_inicio
                
                # Eliminamos los paréntesis y separamos las coordenadas
                coordenadas_lista = ruta3['inicio'].strip('()').split(', ')
                latitud, longitud = map(float, coordenadas_lista)

                # Creamos el diccionario
                ruta3['inicio'] = {'lat': latitud, 'lng': longitud}
                coordenadas2 = ruta3['inicio'] # Asegúrate de tener los campos reales

                if (coordenadas1['lat'] != coordenadas2['lat'] and coordenadas1['lng'] != coordenadas2['lng']):
                    ruta3['cercania'] = calcularDistancia(coordenadas1, coordenadas2)
                    ruta3['cercania'] = numero_redondeado = round(ruta3['cercania'], 2)
                    
            rutas_con_coordenadas = sorted(rutas_con_coordenadas, key=lambda x: x['cercania'])
            
            rutas_con_coordenadas.pop(0)
            
            # Convierte rutas_con_coordenadas a formato JSON
            rutas_json = json.dumps(rutas_con_coordenadas)
            
            num_rutas = len(rutas_con_coordenadas)
            
            #Busqueda wiki
        
            info_wiki = []
            wikipedia.set_lang("es")  
            
            print(len(lugares_a_buscar)) 
        
        
            if len(lugares_a_buscar) > 0:
        
        
                
                for lugar in lugares_a_buscar:
                    
                    if lugar:
                    
                        try:

                            busqueda = wikipedia.search(lugar, results=1)
                            result = wikipedia.page(busqueda[0])
                            
                            info_wiki.append({'lugar': lugar, 'info': result})  
                            
                            
                        except wikipedia.exceptions.DisambiguationError as e:
                            
                    
                            
                            x = 0
                            
                            if e.options[x] == '':
                                x = x + 1
                            
                            result = wikipedia.page(e.options[x])
                            #result2 = wikipedia.page(e.options[x + 1])
                                        
                            info_wiki.append({'lugar': lugar, 'info': result})  
                            #info_wiki.append({'lugar': lugares_a_buscar[va + 1], 'info': result2})   
                            
                            
            #print(info_wiki) 
        
                        
        return render(request, 'rutas/ruta.html', {'title': ruta, 
                                                'ruta': ruta,
                                                'wiki_data': info_wiki,
                                                'comentarios': comentarios,
                                                'comentarios_json':comentarios_json,
                                                'rutas_json':rutas_json,
                                                'rutas_con_coordenadas':rutas_con_coordenadas,
                                                'num_rutas': num_rutas,
                                                'track': ruta.puntos, 
                                                'imagenes': imagenes,
                                                'imagenes_serializable':imagenes_serializable,
                                                'videos': videos,
                                                'videos_serializable': videos_serializable,
                                                'max_alt': ruta.alt_max,
                                                'min_alt': ruta.alt_min,
                                                'des_pos': ruta.desnivel_pos,
                                                'des_neg': ruta.desnivel_neg,
                                                'longitud': ruta.distancia_total,
                                                'altitudes': ruta.altitudes,
                                                'distances': ruta.distancias,
                                                'tiempo_total': ruta.tiempo_total,
                                                'clima': tiempo,
                                                'municipioMeteo': municipioMeteo,
                                                'fechaRuta': ruta.fecha_realizacion})
        
    
    except Ruta.DoesNotExist:
        
        print(f"La ruta con id={ruta_id} no existe.")
                
        redirect_url = '/rutas'
        return redirect(redirect_url) 
        
@user_passes_test(lambda u: u.is_authenticated)
def editarRuta_page(request, ruta_id):
    
    ruta = Ruta.objects.get(id=ruta_id)  

    title = "Editar descripción de: '{}'".format(ruta)
    
    if request.method == 'POST':
        
        descripcion = request.POST.get('descripcion')
        
        if ruta.descripcion != descripcion:
           
            rutaupdate = Ruta.objects.filter(id=ruta_id).update(descripcion=descripcion)
        
            redirect_url = '/ruta/{}?updatedDesc'.format(ruta_id)
            return redirect(redirect_url)
        
    
    return render(request, 'rutas/editar-ruta.html', {'title': title, 'ruta': ruta, 'idRuta': ruta_id})
  
@user_passes_test(lambda u: u.is_authenticated)
def eliminarRuta_page(request, ruta_id):
    
    ruta = Ruta.objects.get(id=ruta_id)
    
    nombre_archivo = str(ruta) + '.gpx'
    
    #Eliminar fisicamente el track.gpx 
    ruta_track = os.path.join(settings.DIR_MEDIA, 'tracks', nombre_archivo)
    #print(ruta_track)
    
    try:
        os.remove(ruta_track)
        
    except OSError as e:
        print(f'Error al borrar el track: {e.strerror}')

    
    #buscar y borrar fisiamente las imagenes
    imagenes = Imagen.objects.filter(ruta=ruta)
    for imagen in imagenes:
        path_image = imagen.imagen.url.replace("/media/", "")
        ruta_imagen = os.path.join(settings.DIR_MEDIA, path_image)
        #print(ruta_imagen)
        
        try:
            os.remove(ruta_imagen)
            
        except OSError as e:
            print(f'Error al borrar la imagen: {e.strerror}')
        
        
    #buscar y borrar fisiamente los videos
    videos = Video.objects.filter(ruta=ruta)
    for video in videos:
        path_video = video.video.url.replace("/media/", "")
        path_miniatura = path_video.replace(".mp4", "_thumbnail.png")
        ruta_video = os.path.join(settings.DIR_MEDIA, path_video)
        ruta_miniatura = os.path.join(settings.DIR_MEDIA, path_miniatura)
        
        #print(ruta_video)
        #print(ruta_miniatura)
        
        try:
            os.remove(ruta_video)
            os.remove(ruta_miniatura)
            
        except OSError as e:
            print(f'Error al borrar el video o miniatura: {e.strerror}')
    
    
    
    # Finalmente, eliminar la instancia de Ruta y con esto, las imagenes y videos asociados a la vez
    ruta.delete()
    
    redirect_url = '/rutas'
    return redirect(redirect_url)
    
      
#Otras funciones
@require_GET
@user_passes_test(lambda u: u.is_authenticated)
def cargar_track(request, filename): 
    
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
 
    filepath = BASE_DIR + '\\tracks\\' + filename
    
    with open(filepath, 'rb') as gpx_file:
        response = HttpResponse(gpx_file.read(), content_type='application/xml')
        response['Content-Disposition'] = 'attachment; filename=filename'
        return response

def subirTrack(track):
    
    if track:
        
        archivo_nombre = track.name
        # Usamos os.path.splitext para separar el nombre de la extensión
        nombre, extension = os.path.splitext(archivo_nombre)
        archivo_nombre = archivo_nombre.replace(' ', '-')
        url_archivo = os.path.join(settings.DIR_MEDIA, 'tracks', archivo_nombre) 
        
        #subir archivo a carpeta
        with open(url_archivo, 'wb') as destination:
            for chunk in track.chunks():
                destination.write(chunk)
                                
                
        # Parsear el archivo GPX
        tree = ET.parse(url_archivo)
        root = tree.getroot()
                
        
        # Buscar la etiqueta <desc>
        desc_element = root.find(".//{http://www.topografix.com/GPX/1/1}desc")
        # Buscar la etiqueta <name>
        name_element = root.find(".//{http://www.topografix.com/GPX/1/1}name")
        # Buscar la etiqueta <time>
        time_element = root.find(".//{http://www.topografix.com/GPX/1/1}time")
        # Buscar punto de origen
        point_element = root.find(".//{http://www.topografix.com/GPX/1/1}trkpt")
        # Buscar desnivel pos
        ascent_element = root.find(".//{http://www.garmin.com/xmlschemas/TrackStatsExtension/v1}Ascent")
        # Buscar desnivel neg
        descent_element = root.find(".//{http://www.garmin.com/xmlschemas/TrackStatsExtension/v1}Descent")
        
        # Obtiene los atributos de latitud y longitud        
        palabras_clave = obtener_palabras_clave(point_element.attrib['lat'], point_element.attrib['lon'])
        palabras_clave = ''
        descripcion = None
        time = None
        
                
        if desc_element is not None:
            # Obtener el contenido de <desc>
            descripcion = desc_element.text
            
        elif  name_element is not None:
            descripcion = name_element.text
            
            descripcion = descripcion.replace('Track actual', nombre)
            
            
        if time_element.text is not None:
            # Obtener el contenido de <desc>
            time = time_element.text
            # Convertir la cadena a un objeto datetime
            fecha_datetime = datetime.strptime(time, "%Y-%m-%dT%H:%M:%SZ")
            
            # Obtener solo la fecha en formato "YYYY-MM-DD"
            time = fecha_datetime.strftime("%Y-%m-%d")
                    
        
        #Recoger distancia_total, desnivel_pos, desnivel_neg, tiempo_total, alt_max, alt_min y puntos
        ruta_str = str(archivo_nombre.split('.')[0])
        ruta_name = (ruta_str + '.gpx').lower()
        municipioMeteo = None 
        municipio = None
        
        
        #ruta_path = os.path.join(settings.BASE_DIR, 'media', 'tracks', ruta_name) debug
        ruta_path = os.path.join(settings.DIR_MEDIA, 'tracks', ruta_name)
        
        with open(ruta_path, 'r') as gpx_file:
            
            try:
                gpx = gpxpy.parse(gpx_file)
            except UnicodeDecodeError as e:
                # Obtener el carácter que no pudo ser decodificado
                problematic_character = e.object[e.start:e.end]
                gpx_file.close()
                os.remove(ruta_path)  # Elimina el archivo subido recientemente
                
                return False
                                

            # Aquí puedes obtener la información del track, como puntos de latitud y longitud
            track_points = [(p.latitude, p.longitude) for p in gpx.tracks[0].segments[0].points]
            
            # Obtener todos los puntos de altitud
            altitudes = [p.elevation for p in gpx.tracks[0].segments[0].points]
            
            # tiempo empleado
            # Inicializar tiempo_total en 0
            tiempo_total = 0

            # Iterar a través de los segmentos y pistas para calcular el tiempo total
            for track in gpx.tracks:
                for segment in track.segments:
                    # Obtener el tiempo de inicio y fin del segmento
                    tiempo_inicio = segment.points[0].time
                    tiempo_fin = segment.points[-1].time

                    # Calcular la diferencia de tiempo y sumarla al tiempo total
                    diferencia_tiempo = tiempo_fin - tiempo_inicio
                    tiempo_total += diferencia_tiempo.total_seconds()
                                        
            tiempo_total_formateado = convertir_tiempo(tiempo_total)
            
            
            # Reducir los puntos dependiendo de los puntos originales
            
            if len(track_points) > 1000 and len(track_points) < 1500:
                altitudes_red = altitudes[::12]
            elif len(track_points) > 1499 and len(track_points) < 2000:
                altitudes_red = altitudes[::20]
            elif len(track_points) > 1999:
                altitudes_red = altitudes[::28]
            else:
                altitudes_red = altitudes
            
            altitudes_reales = altitudes
            
            #Obtener primer punto para saber en que municipio nos encontramos en este track
            primer_punto = track_points[0]
            
            
        #guardar puntos de distancias, calcular longitud
        distances = [0]
        for i in range(1, len(track_points)):
            distancia = geodesic(track_points[i - 1], track_points[i]).meters
            

            distances.append(distances[-1] + distancia)
            
            
        #calcular longitud del track  en km
        longitud_total = round(distances[-1] / 1000, 1)
        
        # Verificar si se encontró el elemento
        if ascent_element is not None:
            # Obtener el texto dentro de la etiqueta
            ascent_value = ascent_element.text
            # Convertir el valor a un entero (si es necesario)
            desnivel_positivo = int(ascent_value) if ascent_value is not None else None
        else:
            # En caso de que la etiqueta no se encuentre
            #calcular desnivel positivo acumulado esto tiene que ser con los puntos reducidos
            desnivel_positivo = 0
            for i in range(1, len(altitudes_red)):
                diferencia_altitud = altitudes_red[i] - altitudes_red[i - 1]
                if diferencia_altitud > 0:
                    desnivel_positivo += diferencia_altitud
                    
            desnivel_positivo = round(desnivel_positivo)
                
        # Verificar si se encontró el elemento
        if descent_element is not None:
            # Obtener el texto dentro de la etiqueta
            descent_value = descent_element.text
            # Convertir el valor a un entero (si es necesario)
            desnivel_negativo = int(descent_value) if descent_value is not None else None
        else:
            #calcular desnivel negativo acumulado esto tiene que ser con los puntos reducidos
            desnivel_negativo = 0
            for i in range(1, len(altitudes_red)):
                diferencia_altitud = altitudes_red[i - 1] - altitudes_red[i]
                if diferencia_altitud > 0:
                    desnivel_negativo += diferencia_altitud        
                    
            desnivel_negativo = round(desnivel_negativo)
                
        
        # Calcular la altitud máxima y mínima
        altitud_maxima = round(max(altitudes))
        altitud_minima = round(min(altitudes))
        
        
        ruta = Ruta()
        
        ruta.nombre = archivo_nombre.split('.')[0]
        if descripcion == None:
            descripcion = 'Track realizado el {}'.format(time)
        ruta.descripcion = descripcion
        ruta.fecha_realizacion = time
        ruta.claves = palabras_clave
        ruta.trak = os.path.join('tracks', archivo_nombre)
        ruta.distancia_total = longitud_total
        ruta.desnivel_pos = desnivel_positivo
        ruta.desnivel_neg = desnivel_negativo
        ruta.alt_max = altitud_maxima
        ruta.alt_min = altitud_minima
        ruta.inicio = str(primer_punto)
        ruta.tiempo_total = tiempo_total_formateado
        ruta.puntos = str(track_points)
        ruta.altitudes = str(altitudes_reales)
        ruta.distancias = str(distances)

        ruta.save()
                
        return True
             
def subirImagenesOVideos(ruta, imagenes, videos):
    
    if imagenes:
            
        for archivo in imagenes:
                 
            archivo_nombre = archivo.name
            url_imagen = os.path.join(settings.DIR_MEDIA, 'images', archivo_nombre) 
                            
            #bajar la calidad de la imagen
            if archivo.size > 800000:
                image = cv2.imdecode(np.fromstring(archivo.read(), np.uint8), cv2.IMREAD_COLOR)
                nueva_calidad = 20  # Cambia esto para ajustar la calidad
                encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), nueva_calidad]
                _, imagen_reducida = cv2.imencode('.jpg', image, encode_param)
                
                #subir archivo a carpeta
                with open(url_imagen, 'wb') as f:
                    f.write(imagen_reducida.tobytes())
            
            else:
                
                #subir archivo a carpeta
                with open(url_imagen, 'wb') as destination:
                    for chunk in archivo.chunks():
                        destination.write(chunk)
            
                        
            imagen = Imagen()
            imagen.ruta = ruta
            imagen.imagen = os.path.join('images', archivo_nombre)
            
            imagen.save()   
                
                
    if videos:     
        
        for archivo in videos:  
            
            thumbnail_time = 2  # Tiempo en segundos para capturar la miniatura
            thumbnail_size_v = (400, 600)  # Tamaño deseado de la miniatura (ancho, alto)
            thumbnail_size_h = (400, 200)
                    
            archivo_nombre = archivo.name
            output_thumbnail = os.path.join(settings.DIR_MEDIA, 'videos')
            url_video = os.path.join(settings.DIR_MEDIA, 'videos',  archivo_nombre) 
            
            #subir archivo a carpeta
            with open(url_video, 'wb') as destination:
                for chunk in archivo.chunks():
                    destination.write(chunk)
                    
            thumbnail_path = os.path.join(output_thumbnail, f"{os.path.splitext(url_video)[0]}_thumbnail.png")

            video_clip = VideoFileClip(url_video)        
            video_duration = video_clip.duration
            thumbnail_time = min(thumbnail_time, video_duration)
                    
            thumbnail_frame = video_clip.get_frame(thumbnail_time)

            video_rotation = video_clip.rotation
            
            # Redimensionar la miniatura en función de la orientación del video
            thumbnail_size = thumbnail_size_h #por defecto verticalmente
            
            if video_rotation == 0:  # Video orientado verticalmente
                thumbnail_size = thumbnail_size_h
            elif video_rotation == 90:
                thumbnail_size = thumbnail_size_v
                
            thumbnail_frame = cv2.resize(thumbnail_frame, thumbnail_size)
            
            # marca de agua
            # Cargar el icono de play
            
            icon_path = os.path.join(settings.STATICFILES_DIRS[0], 'iconos', 'play.png')
            play_icon = cv2.imread(icon_path, cv2.IMREAD_UNCHANGED)
            
            # Definir el nuevo tamaño para el icono de reproducción (ajustar según sea necesario)
            play_icon[:, :, 3] = 255
            nuevo_ancho = int(play_icon.shape[1] * 1.5)  # Aumentar el ancho en un 50%
            nuevo_alto = int(play_icon.shape[0] * 1.5)   # Aumentar el alto en un 50%
            play_icon = cv2.resize(play_icon, (nuevo_ancho, nuevo_alto))
                        
            # Calcular la posición central para el icono de play
            x_offset = (thumbnail_frame.shape[1] - play_icon.shape[1]) // 2
            y_offset = (thumbnail_frame.shape[0] - play_icon.shape[0]) // 2

            # Convertir las imágenes a tipo float32 para la fusión
            thumbnail_frame = thumbnail_frame.astype('float32')
            
            # Crear una máscara de transparencia para el icono
            icon_alpha = play_icon[:, :, 3] / 255.0
            
            # Crear una copia del icono con fondo transparente
            icon_no_bg = play_icon[:, :, 0:3]  # Obtener solo los canales RGB
            icon_no_bg = icon_no_bg.astype('float32')  # Convertir a tipo float32
            icon_no_bg *= icon_alpha[:, :, np.newaxis]  # Aplicar la máscara de transparencia

            # Aplicar la fusión con transparencia
            alpha = 0.9  # Porcentaje de transparencia (ajusta según tus necesidades)
            
            # Realizar la fusión
            fused_icon = cv2.addWeighted(thumbnail_frame[y_offset:y_offset+play_icon.shape[0], x_offset:x_offset+play_icon.shape[1]], alpha, icon_no_bg, 1 - alpha, 0)

            # Colocar la imagen fusionada de nuevo en la imagen principal
            thumbnail_frame[y_offset:y_offset+play_icon.shape[0], x_offset:x_offset+play_icon.shape[1]] = fused_icon

            # Guardar la imagen fusionada
            cv2.imwrite(thumbnail_path, cv2.cvtColor(thumbnail_frame, cv2.COLOR_RGB2BGR))
                        
            video_clip.reader.close()
                        
            
            video = Video()
            
            video.ruta = ruta
            video.video = os.path.join('videos', archivo_nombre)
            
            video.save()   
                    
def convertir_tiempo(tiempo_total):
    horas = int(tiempo_total // 3600)
    minutos = int((tiempo_total % 3600) // 60)
    segundos = int(tiempo_total % 60)
    return f"{horas:02}:{minutos:02}:{segundos:02}"
     
def obtener_localidades(latitud, longitud):
    url = f'https://maps.googleapis.com/maps/api/geocode/json?latlng={latitud},{longitud}&key={settings.API_KEY_GOOGLE}'
    response = requests.get(url)
    data = response.json()
    localidades = []
    
    if data['status'] == 'OK':
                
        for result in data['results']:
            
            for address_component in result['address_components']:
                if 'locality' in address_component['types']:  
                    
                    localidades.append(address_component['long_name']) 
                    
        for result in data['results']:
            
            for address_component in result['address_components']:
                #print(address_component)
                if 'administrative_area_level_2' in address_component['types']:  
                    
                    localidades.append(address_component['long_name'])

        return localidades
        
    return None

def obtener_palabras_clave(latitud, longitud):
    url = f'https://maps.googleapis.com/maps/api/geocode/json?latlng={latitud},{longitud}&key={settings.API_KEY_GOOGLE}'
    response = requests.get(url)
    data = response.json()
    valores_unicos = []
    
    if data['status'] == 'OK':
                    
        for result in data['results']:
            
            for address_component in result['address_components']:
                if address_component['long_name'] not in valores_unicos:
                    valores_unicos.append(address_component['long_name'])
                
        # Usando el método join para unir los elementos de la lista con comas y agregar corchetes
        #valores_unicos_string = '[' + ', '.join(f"'{item}'" for item in valores_unicos) + ']'
        valores_unicos_string = ',: '.join(valores_unicos)

        return valores_unicos_string
        
    return None
    
def elTiempo(codigo):
            
    url = 'https://opendata.aemet.es/opendata/api/prediccion/especifica/municipio/diaria/{}/?api_key={}'.format( codigo, settings.API_KEY_AEMET)
            
    response = requests.get(url)
    

    if response.status_code == 200:  # Verifica si la solicitud fue exitosa (código de estado 200)
        data = response.json()  # Convierte la respuesta a un diccionario Python
        if data['estado'] == 200:
            datos_url = data['datos']
            #print(datos_url)
            # Ahora puedes utilizar 'data' en tu vista
            return datos_url  # Si deseas devolver la respuesta como JSON en tu propia vista
        else:
            
            #no hay 
            return 'KO'
            

    else:
        return HttpResponse(f'Error al hacer la solicitud: {response.status_code}')

def visualizarRuta(request):
    
    data = json.loads(request.body)  
        
    ruta = Ruta.objects.get(nombre=data['ruta'])  
    
    ruta_con_coordenadas = []

    ruta_str = str(ruta.nombre)
    ruta_name = (ruta_str + '.gpx').lower() 
    
    ruta_path = os.path.join(settings.DIR_MEDIA, 'tracks', ruta_name)
    
    with open(ruta_path, 'r') as gpx_file:
        gpx = gpxpy.parse(gpx_file)
        first_point = gpx.tracks[0].segments[0].points[0]  # Obtiene el primer punto
                
    #inicio_ruta = [first_point.latitude, first_point.longitude]  # Cambiado a lista
    inicio_ruta = {'lat': first_point.latitude, 'lng': first_point.longitude}  # Cambiado a objeto

    ruta_con_coordenadas.append({
        'id': ruta.id,
        'ruta': ruta.nombre,
        'inicio': inicio_ruta,
    })
    

    # Convierte rutas_con_coordenadas a formato JSON
    ruta_json = json.dumps(ruta_con_coordenadas)
    
    
    return JsonResponse(ruta_json, safe=False)
 
def guardarClaves(request):
        
    if request.method == "POST":
        clave_string = request.POST.get('clave_string', '')
        ruta = request.POST.get('ruta', '')
        # Haz lo que necesites con el string en tu vista
        
        rutaupdate = Ruta.objects.filter(nombre=ruta).update(claves=clave_string)
        
    # Devuelve una respuesta JSON si es necesario
        return JsonResponse({'ok': True})
    else:
        return JsonResponse({'ok': False}, status=405)
    
def calcularDistancia(coord1, coord2):
    R = 6371.0  # Radio de la Tierra en kilómetros
    lat1 = radians(coord1['lat'])
    lon1 = radians(coord1['lng'])
    lat2 = radians(coord2['lat'])
    lon2 = radians(coord2['lng'])

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distancia = R * c  # Distancia en kilómetros

    return distancia