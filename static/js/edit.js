let mbAttr = 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, <a href="https://www.mapbox.com/">mapbox</a> ',
    MymbUrl = 'https://api.mapbox.com/styles/v1/js00193/{id}/tiles/256/{z}/{x}/{y}@2x?access_token=pk.eyJ1IjoianMwMDE5MyIsImEiOiJjazN0dnN2aDkwNmwxM21vM2lvNDB4ZzJkIn0.48gtpsBsdD2vLWDVe1dOlQ';

let streets = L.tileLayer(MymbUrl, {
    maxZoom: 20,
    maxNativeZoom: 20,
    id: 'cksldzvyx9x3617pd62xaxskn',
    attribution: mbAttr
});

let orig_latlng = [$("#monster-lat").val(), $("#monster-lng").val()];

let map = L.map('map', {
    center: orig_latlng,
    zoom: 18,
    maxZoom: 20,
    minZoom: 10,
    zoomDelta: 0.25,
    zoomSnap: 0,
    layers: [streets],
    zoomControl: false
});

let marker = L.marker(orig_latlng, {
    draggable: true,
}).addTo(map);

marker.on('drag', function (e) {
    let latlng = e.target.getLatLng();
    console.log(latlng);
    $("#monster-lat").val(Number(latlng.lat));
    $("#monster-lng").val(Number(latlng.lng));
});


$("#upload-thumb, #upload-image").on("click", function (e) {
    e.preventDefault();
    let formData = new FormData();
    let current_work = $(this).attr("name");
    console.log(current_work);
    let file = $(`#monster-${current_work}`)[0].files[0];
    console.log(file);
    formData.append("file", file);
    if (window.location.pathname != "/add") {
        formData.append("current_path", window.location.pathname);
    }
    console.log(formData);
    $.ajax({
        url: '/uploadfile',
        type: "POST",
        data: formData,
        success: function (cb) {
            let _dom = `
            <p>
            <span style="background-image: url('/static/img/monsters/tmp/${cb}')"></span>
            <a href="#" class="image-title" data-image="${cb}">${cb}</a>
            <a href="#" class="btn btn-danger remove-image" data-image="${cb}"><i class="fas fa-trash-alt"></i></a>
            </p>`;
            if (current_work == "thumb")
                $("#monster-thumb-block .image-list").html(_dom);
            else
                $("#monster-image-block .image-list").append(_dom);
            $(`#monster-${current_work}`).val("");
        },
        error: function (cb) {
            alert('發生錯誤！請聯絡管理員！');
        },
        cache: false,
        contentType: false,
        processData: false
    })
});


$(".image-list").on('click', '.remove-image', function (e) {
    $(this).parents("p").remove();
});


$("#monster-data-form").on('submit', function (e) {
    e.preventDefault();
    $("#loading").fadeIn(100);
    let _data = orig_data;
    _data["point"] = [$("#monster-lng").val(), $("#monster-lat").val()];
    _data["name"] = $("#monster-name").val();
    _data["tag"] = $("#monster-tag").val().split(",");
    _data["category"] = $("#monster-category").val();
    _data["element"] = $("#monster-element").val();
    _data["date"] = $("#monster-date").val().split("-");
    _data["local"] = $("#monster-local").val();
    _data["disc"] = $("#monster-disc").val();
    _data["strong"] = $("#monster-strong").val();
    _data["weak"] = $("#monster-weak").val();
    _data["title"] = $("#monster-title").val();
    _data["story"] = $("#monster-story").val();
    _data["thumb"] = $("#monster-thumb-block .image-list p .image-title").data("image");
    _data["image"] = [];
    $("#monster-image-block .image-list p .image-title").each(function () {
        _data["image"].push($(this).data("image"));
    });

    $.ajax({
        type: "POST",
        url: window.location.href,
        data: JSON.stringify(_data),
        success: function (cb) {
            $("#loading").fadeOut(300);
            if (cb == "ok") {
                alert("修改成功！");
                window.location.href = window.location.href.replace("edit", "monster");
            }
            else {
                alert(cb);
            }
        },
        contentType: "application/json"
    });
});