$("#edit-button").on('click', function (e) {
    window.location.href = window.location.href.replace("monster", "edit");
});

$("#elements-help,#elements-help-overlay").on("click", function (e) {
    $("#elements-help-overlay").toggleClass("d-none");
});

$("#comment-add").on("submit", function (e) {
    e.preventDefault();
    let monster_id = $("input[name=monster_id]", this).val();
    let content = $("textarea[name=content]", this).val();
    $.ajax({
        type: 'POST',
        url: '/addcomment',
        data: {
            'monster_id': monster_id,
            'content': content
        },
        success: function() {
            location.reload();
        }
    });
});

$(window).resize(function (e) {
    $("#carousel .carousel-item video").height($("#carousel .carousel-item video").width());
});
$(window).resize();