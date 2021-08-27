let params = new URLSearchParams(document.location.search.substring(1));
let url_latlng = params.get("latlng", undefined);
if (url_latlng) {
    url_latlng = url_latlng.split(",");
    $("#monster-lat").val(url_latlng[0]);
    $("#monster-lng").val(url_latlng[1]);
} else {
    url_latlng = [24.937602, 121.712626];
}

let mbAttr = 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, <a href="https://www.mapbox.com/">mapbox</a> ',
    MymbUrl = 'https://api.mapbox.com/styles/v1/js00193/{id}/tiles/256/{z}/{x}/{y}@2x?access_token=pk.eyJ1IjoianMwMDE5MyIsImEiOiJjazN0dnN2aDkwNmwxM21vM2lvNDB4ZzJkIn0.48gtpsBsdD2vLWDVe1dOlQ';
let streets = L.tileLayer(MymbUrl, {
    maxZoom: 20,
    maxNativeZoom: 20,
    id: 'cksldzvyx9x3617pd62xaxskn',
    attribution: mbAttr
});

let map = L.map('map', {
    center: url_latlng,
    zoom: 18,
    maxZoom: 20,
    minZoom: 10,
    zoomDelta: 0.25,
    zoomSnap: 0,
    layers: [streets],
    zoomControl: false
});

let marker = L.marker(url_latlng, {
    draggable: true,
}).addTo(map);

marker.on('drag', function(e) {
    let latlng = e.target.getLatLng();
    console.log(latlng);
    $("#monster-lat").val(latlng.lat);
    $("#monster-lng").val(latlng.lng);
});