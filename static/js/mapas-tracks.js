
function renombrarTitulo() {
    var rutaTitle = document.getElementsByClassName('ruta-title');

    for (i = 0; i < rutaTitle.length; i++) {
        rutaTitle[i].innerHTML = rutaTitle[i].innerHTML.replace(/-/g, ' ');
    }

}

function navegarUrl(url) {
    //var loaderGeneralLogado = document.getElementById('loader-general-logado');
    loaderGeneralLogado.style.display = 'block'
    window.location.href = url;
}

function inicializarMapasTracks() {


    var mapas = document.getElementsByClassName('mapas-tracks');

    for (i=0; i< mapas.length; i++) {

        coordenadasBrutas = mapas[i].getAttribute('data-ruta-info')

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
        

        var mapa = new google.maps.Map(document.getElementById(mapas[i].id), {
            center: { lat: avgLat, lng: avgLng }, // Utiliza la media de las coordenadas para centrar el mapa
            zoom: 12,
            mapTypeId: 'hybrid',
            disableDefaultUI: true,
            draggable: false,
            scrollwheel: false,
        });

        var bounds = new google.maps.LatLngBounds();
        //console.log(bounds)

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
            map: mapa,
            icon: 'http://maps.google.com/mapfiles/ms/icons/green-dot.png', // Icono verde
        });

        // Crear marcador rojo en la última coordenada
        var ultimoMarcador = new google.maps.Marker({
            position: coordenadas[coordenadas.length - 1],
            map: mapa,
            icon: 'http://maps.google.com/mapfiles/ms/icons/red-dot.png', // Icono rojo
        });


        trackPath.setMap(mapa);
        mapa.fitBounds(bounds);

    }

}




inicializarMapasTracks();
renombrarTitulo();