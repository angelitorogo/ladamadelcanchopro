//Declarar variables
var googleMapa;
var canvas = document.getElementById('perfilChart');
var ctx = document.getElementById('perfilChart').getContext('2d');
var verticalLineX = -1; 
var distances = JSON.parse(distancesString);
var altitudes = JSON.parse(altitudesString);
var maxValueOfX = Math.max(...distances);
var minValueofY = Math.min(...altitudes);
var maxValueofY = Math.max(...altitudes);
var marcadorActual = null;
var coordenadas = [];
var idAltitud = document.getElementById('id_altitud');
var idDistancia = document.getElementById('id_distancia');
var lineaNegra = document.getElementById('linea_negra');
var lineaNegra2 = document.getElementById('linea_negra2');
var distancia;
var altitud;
var clickedIndex;
var clickedCoordenadas;
var clickedDistance;
var clickedDistanceBruta;
var clickedAltitude;
var myChart = new Chart(ctx, {
    type: 'line',
    data: {
        labels: distances,
        drawActiveElementsOnTop: true,
        datasets: [{
            label: 'Perfil del Track',
            data: altitudes,
            borderColor: 'rgb(255, 240, 75)',
            backgroundColor: 'rgba(210, 180, 140, 0.3)', 
            fill: true,
            borderWidth: 0.5,
            radius: 1,
            pointHoverRadius: 6,
            pointHoverBackgroundColor: 'rgba(0, 13, 255, 0.396)', 
            pointHoverBorderColor: 'rgba(0, 13, 255, 0.396)',
            cubicInterpolationMode: 'monotone'
        }]
    },
    options: {
        responsive: true,
        animation: false,
        maintainAspectRatio: false,
        scales: {
            x: {
                type: 'linear',
                max: maxValueOfX,
                position: 'bottom',
                title: {
                    display: true,
                    text: 'Distancia (metros)'
                },
                grid: {
                    display: false, 
                }
            },
            y: {
                type: 'linear',
                title: {
                    display: true,
                    text: 'Altitud (metros)'
                },
                grid: {
                    display: false, 
                },
            }
        },
        interaction: {
            mode: 'index',
            intersect: false, 
        },
        plugins: {
            tooltip: {
                enabled: false, 
                usePointStyle: true,
                callbacks: {
                    title: function (tooltipItems) {
                        tooltipItems[0].label = tooltipItems[0].label.replace('.',''); //si es mas de 9999 llevara un punto
                        let distancia = (parseFloat(tooltipItems[0].label)/1000).toFixed(2);
                        return 'Distancia: ' + distancia + ' Km';
                    },
                    label: function (tooltipItem) {
                        return 'Altitud: ' + parseFloat(tooltipItem.formattedValue).toFixed(0) + ' m';
                    }
                }
            },
            
        },
        onHover: (event, chartElements) => {

            if (chartElements.length > 0) {
                
                clickedIndex = chartElements[0].index;
                clickedCoordenadas = coordenadas[clickedIndex];
                clickedDistance = distances[clickedIndex];
                clickedDistanceBruta = distances[clickedIndex];
                clickedAltitude = altitudes[clickedIndex];
                alturaLinea = chartElements[0].element.y;
                baseLinea = chartElements[0].element.x;

                baseLinea = (baseLinea / 10) - 2;

                distancia = (parseFloat(clickedDistance)/1000).toFixed(1) + 'km';
                altitud = parseFloat(clickedAltitude).toFixed(0) + 'm';

                idAltitud.classList.remove('no-mostrar');
                idDistancia.classList.remove('no-mostrar');
                lineaNegra.classList.remove('no-mostrar');
                lineaNegra2.classList.remove('no-mostrar');

                idDistancia.style.left = baseLinea + 'rem';
                idDistancia.innerHTML = distancia;
                idAltitud.style.left = baseLinea + 'rem';
                idAltitud.innerHTML = altitud;
                lineaNegra.style.left = (baseLinea) + 'rem';
                lineaNegra2.style.left = (baseLinea + 3.9) + 'rem';

                marcadorActual = crearOActualizarMarcador(marcadorActual, clickedCoordenadas);
                //console.log(clickedDistanceBruta)
                //console.log(baseLinea)
                
                

            }

        },
        onClick: (event, chartElements) => {
        }
    }
});
var imagenes;
var videos;
var fileInput = document.getElementById('id_imagenes');
var videoInput = document.getElementById('id_videos');
var imagenError = document.getElementById('error-imagenes');
var videoError = document.getElementById('error-videos');
var successUpload = document.getElementById('success-upload');
const submitButton = document.getElementById('submitButton');
const myForm = document.getElementById('myForm');
var loader = document.getElementById('loader');
var loaderTiempo = document.getElementById('loader-tiempo');
var miniaturas = document.getElementsByClassName('miniaturas')
var imagenCarrusel = document.getElementById('imagenCarrusel');
var videoCarrusel = document.getElementById('videoCarrusel');
var loaderCarrusel = document.getElementById('loader-carrusel');
var minisaturasArchivos = [];
var archivosCarrusel = [];
var archivos = [];
var archivoBuscar;
var miniaturasImagenes = [];
var miniaturasVideos = [];
var pos = 0;
var viendo = '';
var arrayImagenesString = imagenesString.replace(/'/g, "\"");
var arrayVideosString = videosString.replace(/'/g, "\"");
var imagenes = JSON.parse(arrayImagenesString);
var videos = JSON.parse(arrayVideosString);

function navegarUrl(url) {
    var loaderGeneralLogado = document.getElementById('loader-general-logado');
    loaderGeneralLogado.style.display = 'block'
    window.location.href = url;
}

function renombrarTitulo() {
    var rutaTitle = document.getElementById('name-ruta');

    rutaTitle.innerHTML = rutaTitle.innerHTML.replace(/-/g, ' ');

}

//Funciones
function miniaturasPath() {
    for(i=0;i<miniaturas.length;i++) {
        var miniaturaUrl = miniaturas[i].src;
        miniaturaUrl = miniaturaUrl.replace('.mp4', '_thumbnail.png');
        miniaturas[i].src = miniaturaUrl;
    }
}

function inicializarMapaTrack() {

    var mapa = document.getElementById('mapa');
    
    

    coordenadasBrutas = mapa.getAttribute('data-ruta-info')

    // Eliminamos los caracteres no deseados y dividimos el string en coordenadas individuales
    var arrayCoordenadas = coordenadasBrutas.replace(/[\[\]]/g, "").split(", ")
    
    const coordenadas = [];

    for (let i = 0; i < arrayCoordenadas.length; i += 2) {
        const lat = parseFloat(arrayCoordenadas[i].replace('(', ''));
        const lng = parseFloat(arrayCoordenadas[i + 1].replace(')', ''));
        coordenadas.push({ lat, lng });
    }

    // Calcular las coordenadas promedio
    var sumLat = 0;
    var sumLng = 0;
    for (let i = 0; i < coordenadas.length; i++) {
        sumLat += coordenadas[i].lat;
        sumLng += coordenadas[i].lng;
    }
    const avgLat = sumLat / coordenadas.length;
    const avgLng = sumLng / coordenadas.length;
    

    googleMapa = new google.maps.Map(document.getElementById('mapa'), {
        center: { lat: avgLat, lng: avgLng }, // Utiliza la media de las coordenadas para centrar el mapa
        zoom: 12,
        mapTypeId: 'hybrid',
    });

    var bounds = new google.maps.LatLngBounds();

    // Agrega las coordenadas al objeto 'bounds'
    for (var j = 0; j < coordenadas.length; j++) {
        bounds.extend(coordenadas[j]);
    }
        

    var trackPath = new google.maps.Polyline({
        path: coordenadas,
        geodesic: true,
        strokeColor: '#FFFF00',
        strokeOpacity: 1.0,
        strokeWeight: 3
    });


    // Crear marcador verde en la primera coordenada
    var primerMarcador = new google.maps.Marker({
        position: coordenadas[0],
        map: googleMapa,
        icon: 'http://maps.google.com/mapfiles/ms/icons/green-dot.png', // Icono verde
    });

    // Crear marcador rojo en la última coordenada
    var ultimoMarcador = new google.maps.Marker({
        position: coordenadas[coordenadas.length - 1],
        map: googleMapa,
        icon: 'http://maps.google.com/mapfiles/ms/icons/red-dot.png', // Icono rojo
    });


    trackPath.setMap(googleMapa);
    googleMapa.fitBounds(bounds);

}

function prepararDatos() {

    var mapa = document.getElementById('mapa');

    coordenadasBrutas = mapa.getAttribute('data-ruta-info')

    var arrayCoordenadas = coordenadasBrutas.replace(/[\[\]]/g, "").split(", ")
    
    

    for (let i = 0; i < arrayCoordenadas.length; i += 2) {
        const lat = parseFloat(arrayCoordenadas[i].replace('(', ''));
        const lng = parseFloat(arrayCoordenadas[i + 1].replace(')', ''));
        coordenadas.push({ lat, lng });
    }

}

//Llamada a funciones
prepararDatos();
inicializarMapaTrack();
miniaturasPath();
renombrarTitulo();


function crearOActualizarMarcador(marcador, coordenadas) {

    //console.log('crear o actualizar marcador')

    if (marcador) {
        marcador.setPosition(coordenadas);
    } else {
        marcador = new google.maps.Marker({
            position: coordenadas,
            map: googleMapa,
            icon: iconoRedondoAzul,
        });
    }
    return marcador;
}

function ImagenesSeleccionadas(event) {

    if (successUpload) {
        successUpload.classList.add('no-mostrar');
    }

    imagenes = event.target.files

    if (imagenes.length || imagenes.length !=0) {

        if (imagenError.classList.contains('no-mostrar')) {
            imagenError.classList.remove('no-mostrar');
        }

        for (i=0; i < imagenes.length; i++) {
            if (imagenes[i]) {
                
                const validImageTypes = ['image/jpeg', 'image/png'];
                if (!validImageTypes.includes(imagenes[i].type)) {
                    
                    imagenError.classList.remove('no-mostrar');
                    
                    fileInput.value = ''; // Limpiar la selección del archivo no válido
                    return;

                } else {
                    if (!imagenError.classList.contains('no-mostrar')) {
                        imagenError.classList.add('no-mostrar');
                    }
                }
    
            }
        }

    }

}

function videosSeleccionados(event) {

    if (successUpload) {
        successUpload.classList.add('no-mostrar');
    }

    videos = event.target.files

    if (videos.length || videos.length !=0) {
        if (videoError.classList.contains('no-mostrar')) {
            videoError.classList.remove('no-mostrar');
        }
        for (i=0; i< videos.length; i++) {
            if (videos[i]) {
                const validVideoTypes = ['video/mp4'];
                if (!validVideoTypes.includes(videos[i].type)) {
                    videoError.classList.remove('no-mostrar');
                    videoInput.value = ''; // Limpiar la selección del archivo no válido
                } else {
                    if (!videoError.classList.contains('no-mostrar')) {
                        videoError.classList.add('no-mostrar');
                    }
                }
    
            }
        }

    }
    
}

function checkFiles() {

    let hayimagenes = false
    let hayvideos = false

    if (imagenes) {
        if (imagenes.length != 0) {
            hayimagenes = true
        }
    }

    if (videos) {
        if (videos.length != 0) {
            hayvideos = true
        }
    }

    if ( hayimagenes || hayvideos) {

        submitButton.removeAttribute('disabled');
    } else {
        submitButton.setAttribute('disabled', 'disabled');

    }
}

function subirArchivo() {
    loader.classList.add('mostrar');
}

//Eventos
canvas.addEventListener('mouseout', () => {
    
    //marcadorActual = crearOActualizarMarcador(marcadorActual, coordenadas[0]);
    idAltitud.classList.add('no-mostrar');
    idDistancia.classList.add('no-mostrar');
    lineaNegra.classList.add('no-mostrar');
    lineaNegra2.classList.add('no-mostrar');

    marcadorActual = crearOActualizarMarcador(marcadorActual, {lat:0, lng:0});

});

if (myForm) { //Si no es staff, no mostrara la subida de archivos, sino datos del tiempo
    myForm.addEventListener('submit', function(event) {
        if (!imagenes && !videos) {
            event.preventDefault();
        }
    });

    fileInput.addEventListener('change', checkFiles);

    videoInput.addEventListener('change', checkFiles);


}


//console.log(imagenes)
//console.log(videos)

function carousel(imagen, video) {

    archivosCarrusel = []
    pos=0

    if (imagen) {

        for (i=0;i< imagenes.length; i++) {
            miniaturasImagenes.push(imagenes[i].imagen);
            archivosCarrusel[i] = '/media/' + miniaturasImagenes[i].replace('\\', '/')
        }

        for (i=0;i< videos.length; i++) {
            miniaturasVideos.push(videos[i].video.replace('.mp4' ,'_thumbnail.png'));
            archivosCarrusel[imagenes.length + i] =  '/media/' + miniaturasVideos[i].replace('\\', '/')

        }

        archivoBuscar = imagen;

    } else {

        for (i=0;i< videos.length; i++) {
            miniaturasVideos.push(videos[i].video.replace('.mp4' ,'_thumbnail.png'));
            archivosCarrusel[i] =  '/media/' + miniaturasVideos[i].replace('\\', '/')

        }

        for (i=0;i< imagenes.length; i++) {
            miniaturasImagenes.push(imagenes[i].imagen);
            archivosCarrusel[ videos.length + i] = '/media/' + miniaturasImagenes[i].replace('\\', '/')
        }

        var miniaturaVideo = video.replace('.mp4' ,'_thumbnail.png');
        archivoBuscar = miniaturaVideo

    }
    
    const posicionTotal = archivosCarrusel.indexOf(archivoBuscar);

    if (posicionTotal !== -1) {
        const parte1 = archivosCarrusel.slice(0, posicionTotal); // Parte antes del elemento buscado
        const parte2 = archivosCarrusel.slice(posicionTotal + 1); // Parte después del elemento buscado
        archivos = [archivoBuscar, ...parte2, ...parte1];
        
    } 

    //SAber si es imagen o video para mostrar img o video en html
    if (archivos[pos].includes('images')) {

        viendo = 'imagen';

        loaderCarrusel.classList.remove('mostrar');

        videoCarrusel.pause();
        imagenCarrusel.src = archivos[pos];

        imagenCarrusel.classList.remove('no-mostrar');
        videoCarrusel.classList.add('no-mostrar')

    } else {

        viendo = 'video';

        videoCarrusel.src = archivos[pos].replace('_thumbnail.png','.mp4');

        imagenCarrusel.classList.add('no-mostrar');
        loaderCarrusel.classList.add('mostrar');

        videoCarrusel.addEventListener('canplaythrough', function() {

            if (viendo == 'video') {
                videoCarrusel.classList.remove('no-mostrar');
                loaderCarrusel.classList.remove('mostrar');
                videoCarrusel.play();
            }

        });


    }

    //Mostrar modal
    modalContainer.style.display = 'flex';

}

function adelanteAtras(i) {
    
    videoCarrusel.classList.add('no-mostrar')

    pos = pos + i;

    if (pos == archivos.length) {
        pos = 0;
    } else if ( pos == -1) {
        pos = archivos.length -1;
    }


    //SAber si es imagen o video para mostrar img o video en html
    if (archivos[pos].includes('images')) {

        viendo = 'imagen';

        loaderCarrusel.classList.remove('mostrar');

        videoCarrusel.pause();
        imagenCarrusel.src = archivos[pos];

        imagenCarrusel.classList.remove('no-mostrar');
        videoCarrusel.classList.add('no-mostrar')

    } else {

        viendo = 'video';

        videoCarrusel.src = archivos[pos].replace('_thumbnail.png','.mp4');

        imagenCarrusel.classList.add('no-mostrar');
        loaderCarrusel.classList.add('mostrar');

        videoCarrusel.addEventListener('canplaythrough', function() {

            if (viendo == 'video') {
                videoCarrusel.classList.remove('no-mostrar');
                loaderCarrusel.classList.remove('mostrar');
                videoCarrusel.play();
            }

        });

        

    }

}

function cerrarModal() {
    videoCarrusel.pause();
    modalContainer.style.display = 'none';
    //window.location.reload();
}
