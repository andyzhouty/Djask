let main = document.getElementsByTagName("main")[0];
let aside = document.getElementsByTagName("aside")[0];
main.setAttribute("style", "margin-left:" + aside.offsetWidth + "px;");

window.onresize = function () {
    main.setAttribute("style", "margin-left:" + aside.offsetWidth + "px;");
}
