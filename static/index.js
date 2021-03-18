let mbAttr = 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, <a href="https://www.mapbox.com/">mapbox</a> ',
  MymbUrl = 'https://api.mapbox.com/styles/v1/js00193/{id}/tiles/256/{z}/{x}/{y}@2x?access_token=pk.eyJ1IjoianMwMDE5MyIsImEiOiJjazN0dnN2aDkwNmwxM21vM2lvNDB4ZzJkIn0.48gtpsBsdD2vLWDVe1dOlQ';
let satellite = L.tileLayer(MymbUrl, { id: 'ckmemz8hn1m4r17t8hu2sd80i', attribution: mbAttr }),
  streets = L.tileLayer(MymbUrl, {
    id: 'ckmel1ml933t517rtlyqru6nh',
    attribution: mbAttr
  });

let mymap = L.map('map', {
  center: [24.937602, 121.712626],
  zoom: 18,
  maxZoom: 18,
  minZoom: 10,
  zoomDelta: 0.25,
  zoomSnap: 0,
  layers: [streets],
  zoomControl: false
});

L.control.zoom({
  position: 'topright'
}).addTo(mymap);

let baseMaps = {
  "空照圖": satellite,
  "街道圖": streets,
};

L.control.layers(baseMaps, null, { position: 'bottomright' }).addTo(mymap);
mymap.addControl(new L.Control.Gps({ position: 'topright' }));

var popup = L.popup().setContent('<p>Hello world!<br />This is a nice popup.</p>');
let test_marker = L.marker([24.937602, 121.712626]).addTo(mymap);
test_marker.bindPopup(popup).openPopup();