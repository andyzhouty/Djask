window.onload = () => {
    let elements = document.getElementsByClassName("time");
    for (let i in elements) {
        let dateString = elements[i].getAttribute("data-time");
        dateString = dateString.replace(" ", "T") + "Z";
        date = new Date(dateString);
        elements[i].innerText = date.toLocaleString();
    }
};
