
document.addEventListener('DOMContentLoaded', function () {
    // Obtiene el elemento por su ID
    const yearSpan = document.getElementById('year');
    // Obtiene el año actual
    const year = new Date().getFullYear();
    // Establece el año como contenido del elemento
    yearSpan.textContent = year;
});

window.onload = function() {
    ocultarSpinner(); // Asegúrate de que esta función exista y oculte el spinner.
};

window.addEventListener('pageshow', function(event) {
    if (event.persisted) {
        // La página fue cargada desde la caché, probablemente mediante el botón de atrás.
        ocultarSpinner();
    }
});

            // Se añade el evento 'pageshow' para manejar tanto cargas iniciales como cargas desde la caché del navegador.
window.addEventListener('pageshow', function(event) {
    // Esto asegura que el spinner se oculte cada vez que la página se muestre.
    ocultarSpinner();
});

document.addEventListener('keydown', function(event) {
    if ((event.key === 'F5') || ((event.ctrlKey || event.metaKey) && (event.key === 'r'))) {
        mostrarSpinner(); // Asume que esta función mostrará el spinner.
    }
});


function mostrarSpinner() {
    document.getElementById('spinner-overlay').style.display = 'block';
}

function ocultarSpinner() {
    document.getElementById('spinner-overlay').style.display = 'none';
}