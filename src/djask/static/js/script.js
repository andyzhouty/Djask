const main = document.getElementsByTagName("main")[0];
const aside = document.getElementsByTagName("aside")[0];
main.setAttribute("style", "margin-left:" + aside.offsetWidth + "px;");

window.onresize = () => {
    main.setAttribute("style", "margin-left:" + aside.offsetWidth + "px;");
}
