let colors = {
    "wind": "#7CAD82",
    "fire": "#EE7839",
    "ground": "#DBB853",
    "water": "#5B9E98"
}

let mbAttr = 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, <a href="https://www.mapbox.com/">mapbox</a> ',
    MymbUrl = 'https://api.mapbox.com/styles/v1/js00193/{id}/tiles/256/{z}/{x}/{y}@2x?access_token=pk.eyJ1IjoianMwMDE5MyIsImEiOiJjazN0dnN2aDkwNmwxM21vM2lvNDB4ZzJkIn0.48gtpsBsdD2vLWDVe1dOlQ';
let satellite = L.tileLayer(MymbUrl, { id: 'ckmemz8hn1m4r17t8hu2sd80i', attribution: mbAttr }),
    streets = L.tileLayer(MymbUrl, {
        maxNativeZoom: 18,
        id: 'ckova8spg0as318mobuqnirjh',
        attribution: mbAttr
    });

function icon_style(color) {
    return `
	color: black;
	background-color: ${color};
	width: 18px;
	height: 18px;
	display: block;
	left: -9px;
	top: -9px;
	position: relative;
	border-radius: 9px;
	border: 1px solid rgba(50,50,50,0.5);`
};

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
L.control.locate({
    position: 'topright'
}).addTo(mymap);

function popupAddNew(latlng) {
    let popLocation = latlng;
    let popup = L.popup({
        'className': 'cloud-popup',
    })
        .setLatLng(popLocation)
        .setContent('開始標記你發現的坪林妖怪!<br>把雲霧移動到發現的地點增加妖怪資料。')
        .openOn(mymap);
}

const search = new GeoSearch.GeoSearchControl({
    style: 'bar',
    searchLabel: '搜尋地點',
    autoClose: true,
    provider: new GeoSearch.OpenStreetMapProvider({
        params: {
            countrycodes: 'TW'
        }
    }),
});
mymap.addControl(search);
mymap.on('geosearch/showlocation', function (e) {
    popupAddNew(e.marker.getLatLng());
});


var popup = `
<h1>醉猴</h1>
<p>哇哈哈</p>
<a href="/monster/1" class="btn btn-warning">詳細資訊</a>
`;
var customPopupOptions = {
    'className': 'cloud-popup'
}
let test_marker = L.marker([24.937602, 121.712626], {
    icon: L.divIcon({
        className: "custom-marker",
        iconAnchor: [0, 0],
        labelAnchor: [0, 0],
        popupAnchor: [60, 8],
        html: `<span style="${icon_style(colors.wind)}" />`
    }),
    closeButton: false,
}).addTo(mymap);

test_marker.bindPopup(popup, customPopupOptions).openPopup();

mymap.on('click', function (e) {
    popupAddNew(e.latlng);
});