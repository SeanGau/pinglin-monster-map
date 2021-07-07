$("#monster-data-form").on('submit', function(e) {
    e.preventDefault();
    $("#loading").fadeIn(100);
    let _data = {
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