window.addEventListener("load", function() {
    const viewBut = document.getElementById("view");
    viewBut.addEventListener("click", action);
})

function action() {
    window.location.href = "database.html";
}
