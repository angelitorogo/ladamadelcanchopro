function localizacion(ip) {
    //console.log('localizando ip')

    fetch(`http://ip-api.com/json/${ip}`)
    .then(response => response.json())
    .then(data => {


        var coordenadas = {
            lat: data.lat,
            lng: data.lon,
        };

        inicializarMapa(coordenadas);
        

    })
    .catch(error => {
        console.error(error);
  });
}

function inicializarMapa(coordenadas) {

    

    var mapa = new google.maps.Map(document.getElementById('mapa'), {
        center: coordenadas,
        zoom: 12
    });

    var bounds = new google.maps.LatLngBounds();
    var infoWindow = new google.maps.InfoWindow();
    const marcador = new google.maps.Marker({
            position: coordenadas,
            map: mapa
    });

}

function ipPublica() {
    //console.log('averiguando ip')

    // Realiza una solicitud HTTP a un servicio externo para obtener la IP pública
    fetch('https://api.ipify.org/?format=json')
    .then(response => response.json())
    .then(data => {
    const ipAddress = data.ip;

    localizacion(ipAddress);
     
    })
    .catch(error => {
    console.error(error);
    });
}

function geolocalizar() {

    if ("geolocation" in navigator) {
        // El navegador soporta geolocalización
        navigator.geolocation.getCurrentPosition(function(position) {
            var latitud = position.coords.latitude;
            var longitud = position.coords.longitude;
    
            var ubicación = { 
                lat: latitud,
                lng: longitud
            };
    
            inicializarMapa(ubicación);
    
        }, function(error) {
            console.log("Error al obtener la ubicación: " + error.message);
            ipPublica();
        });
    
    } else {
    
        ipPublica();
    
    }

}

geolocalizar();


/*
    //Para que esto funcione en el template html, hay que teneer:

    <div>
        <div id="mapa" style="height: 550px;"></div>
    </div>

    <script src="https://maps.googleapis.com/maps/api/js?key=AIzaSyDaXXI2nDL86yCEfI_lXvZ2VekLk1-jBqs"></script>
    <script src="{% static 'js/google.js' %}"></script>

*/
