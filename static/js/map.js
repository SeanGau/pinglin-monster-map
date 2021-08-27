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
        maxZoom: 20,
        maxNativeZoom: 20,
        id: 'cksldzvyx9x3617pd62xaxskn',
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
	border: 2px solid rgba(50,50,50,0.8);`
};


let params = new URLSearchParams(document.location.search.substring(1));
let url_mid = params.get("mid", undefined);
let current_marker = undefined;

let mymap = L.map('map', {
    center: [24.937602, 121.712626],
    zoom: 18,
    maxZoom: 20,
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
        'className': 'cloud-popup add-popup',
        'offset': L.point(90, 10)
    })
        .setLatLng(popLocation)
        .setContent(`
            <a class="disc">開始標記你發現的<br>坪林妖怪！<br>把雲霧移動到發現的地點增加妖怪資料。</a>
            <a class="link" href="/add?latlng=${latlng.lat},${latlng.lng}">點擊 <i class="fas fa-plus"></i></a>
        `)
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

let markersClusterGroup = L.markerClusterGroup({
    maxClusterRadius: 30,
    disableClusteringAtZoom: 18
});

mymap.on('click', function (e) {
    popupAddNew(e.latlng);
});

L.geoJSON(geojson, {
    onEachFeature: function (feature, layer) {
    },
    pointToLayer: function (feature, latlng) {
        let monster_id = feature['properties']['monster_id'];
        let marker = L.marker(latlng, {
            icon: L.divIcon({
                className: "monster-marker",
                iconAnchor: [0, 0],
                labelAnchor: [0, 0],
                popupAnchor: [70, 10],
                html: `<span style="${icon_style(colors[feature['properties']['element']])}" />`
            }),
            closeButton: false,
        });
        let popup = `
        <a class="title">${feature['properties']['name']}</a>
        <div class="image" style="background-image: url('/static/img/monsters/${monster_id}/${feature['properties']['thumb']}')"></div>
        <a href="/monster/${monster_id}" class="link"><i class="fas fa-angle-double-right"></i></a>
        `;
        let customPopupOptions = {
            'className': 'cloud-popup monster-popup'
        }
        marker.bindPopup(popup, customPopupOptions);
        marker.on('click', function (e) {
            const url = new URL(window.location);
            url.searchParams.set("mid", monster_id);
            window.history.replaceState({}, '', url);
            this.openPopup();
        })
        if (url_mid == monster_id) {
            current_marker = marker;
        }
        //markersClusterGroup.addLayer(marker);
        return marker;
    },
}).addTo(mymap);

//mymap.addLayer(markersClusterGroup);

if (current_marker) {
    current_marker.openPopup();
    mymap.fitBounds(L.latLngBounds([current_marker.getLatLng()]));
}