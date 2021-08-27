let mbAttr = 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, <a href="https://www.mapbox.com/">mapbox</a> ',
MymbUrl = 'https://api.mapbox.com/styles/v1/js00193/{id}/tiles/256/{z}/{x}/{y}@2x?access_token=pk.eyJ1IjoianMwMDE5MyIsImEiOiJjazN0dnN2aDkwNmwxM21vM2lvNDB4ZzJkIn0.48gtpsBsdD2vLWDVe1dOlQ';
let streets = L.tileLayer(MymbUrl, {
maxNativeZoom: 18,
id: 'cksldzvyx9x3617pd62xaxskn',
attribution: mbAttr
});
let orig_latlng = [$("#monster-lat").val(), $("#monster-lng").val()];
let map = L.map('map', {
center: orig_latlng,
zoom: 18,
maxZoom: 18,
minZoom: 10,
zoomDelta: 0.25,
zoomSnap: 0,
layers: [streets],
zoomControl: false
});

let marker = L.marker(orig_latlng, {
draggable: true,
}).addTo(map);

marker.on('drag', function(e) {
let latlng = e.target.getLatLng();
console.log(latlng);
$("#monster-lat").val(Number(latlng.lat));
$("#monster-lng").val(Number(latlng.lng));
});


$("#monster-data-form").on('submit', function(e) {
    e.preventDefault();
    $("#loading").fadeIn(100);
    let _data = {
        "point": [$("#monster-lng").val(), $("#monster-lat").val()],
        "name": $("#monster-name").val(),
        "tag": $("#monster-tag").val().split(","),
        "category": $("#monster-category").val(),
        "element": $("#monster-element").val(),
        "date": $("#monster-date").val().split("-"),
        "local": $("#monster-local").val(),
        "disc": $("#monster-disc").val(),
        "strong": $("#monster-strong").val(),
        "weak": $("#monster-weak").val(),
        "title": $("#monster-title").val(),
        "story": $("#monster-story").val()
    };
    $.ajax({
        type: "POST",
        url: window.location.href,
        data: JSON.stringify(_data),
        success: function (cb) {
            $("#loading").fadeOut(300);
            if (cb == "ok") {
                alert("修改成功！");
            }
            else {
                alert(cb);
            }
        },
        contentType: "application/json"
    });
});

$("#image-list .remove-image").on('click', function(e) {
    console.log($(this).data("image"));
});