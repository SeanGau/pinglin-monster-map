AOS.init({
});
window.onload = function () {
    $(".inner-3-text-scroll").scrollLeft(9999);
    if($(location.hash).offset() == undefined) {
        $(window).scrollTop(0);
    }
    else {
        $(window).scrollTop($(location.hash).offset().top);
    }
    $("#loading").fadeOut(300);
};