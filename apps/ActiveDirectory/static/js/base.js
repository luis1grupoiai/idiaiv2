function confirmarSalida() {
    Swal.fire({
        title: '¿Estás seguro?',
        text: "¿Quieres cerrar sesión?",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#3085d6',
        cancelButtonColor: '#d33',
        confirmButtonText: 'Sí'
    }).then((result) => {
        if (result.isConfirmed) {
            window.location.href = "{% url 'salir' %}";
        }
    });
    return false; // Previene la navegación inmediata
}
document.addEventListener('DOMContentLoaded', function () {
    // Obtiene el elemento por su ID
    const yearSpan = document.getElementById('year');
    // Obtiene el año actual
    const year = new Date().getFullYear();
    // Establece el año como contenido del elemento
    yearSpan.textContent = year;
});