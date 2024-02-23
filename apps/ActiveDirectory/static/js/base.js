
document.addEventListener('DOMContentLoaded', function () {
    // Obtiene el elemento por su ID
    const yearSpan = document.getElementById('year');
    // Obtiene el año actual
    const year = new Date().getFullYear();
    // Establece el año como contenido del elemento
    yearSpan.textContent = year;
});