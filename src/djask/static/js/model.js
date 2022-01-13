window.onload = function () {
    let elements = document.getElementsByClassName("time");
    for (let i = 0; i < elements.length; i++) {
        let dateString = elements[i].getAttribute("data-time");
        dateString.replace(" ", "T");
        dateString += "Z";
        date = new Date(dateString);
        elements[i].innerText = date.toLocaleString();
    }
};