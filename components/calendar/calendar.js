(function(){
    if (document.querySelector(".calendar-component")) {
        document.querySelector(".calendar-component").onclick = function(){ alert("Clicked calendar!"); };
    }
})()
    
Toastify({
    text: "Ejemplo de tostada",
    duration: 3000,
    destination: "#",
    newWindow: true,
    close: true,
    gravity: "top", // `top` or `bottom`
    position: "left", // `left`, `center` or `right`
    stopOnFocus: true, // Prevents dismissing of toast on hover
    style: {
        background: "linear-gradient(to right, #00b09b, #96c93d)",
    },
    onClick: function () { } // Callback after click
}).showToast();
    