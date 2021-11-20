$(document).ready(function () {
    $("main").css("margin-left", $("aside").innerWidth());
    $(window).resize(function () {
        $("main").css("margin-left", $("aside").innerWidth());
    })
});
