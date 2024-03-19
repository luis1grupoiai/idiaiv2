$(document).ready(function() {
    var config = {
        "pageLength": 20,
        "language": {
            "lengthMenu": "Mostrar _MENU_ usuarios por página",
            "zeroRecords": "No se encontraron resultados",
            "info": "Mostrando página _PAGE_ de _PAGES_",
            "infoEmpty": "No hay usuarios disponibles",
            "infoFiltered": "(filtrado de _MAX_ registros totales)",
            "search": "Buscar:",
            "paginate": {
                "first": "Primero",
                "last": "Último",
                "next": "Siguiente",
                "previous": "Anterior"
            },
            "loadingRecords": "Cargando...",
            "processing": "Procesando...",
            "emptyTable": "No hay datos disponibles en la tabla",
            "aria": {
                "sortAscending": ": activar para ordenar la columna de manera ascendente",
                "sortDescending": ": activar para ordenar la columna de manera descendente"
            }
        }
    };

    $('#myTable1, #myTable2, #myTable3, #myTable4, #myTable5, #myTable6').DataTable(config);
});

    
$('#modalAlta').on('hidden.bs.modal', function () {
    $('.modal-backdrop').remove();
    document.body.style.overflow = 'auto';
});

function SolicitarAlta(button) {

      var nombre = button.getAttribute('data-nombre');
      var puesto  = button.getAttribute('data-categoria');


      document.getElementById('nombre').value = nombre ;
      document.getElementById('puesto').value = puesto ;

      var modal = new bootstrap.Modal(document.getElementById('modalAlta'));
      modal.show();
}


function AgregarUsuario(button) {

    var nombre = button.getAttribute('data-nombre');
    var nombrePila = button.getAttribute('data-nombrePila');
    var apellidos = button.getAttribute('data-apellidos');
    var puesto = button.getAttribute('data-puesto');
    var nombreSesion = button.getAttribute('data-nombreSesion');
    var nombreCompleto = button.getAttribute('data-nombreCompleto');
    //var email = button.getAttribute('data-email');
    var departamento = button.getAttribute('data-deparamento');
    var distinguishedName = button.getAttribute('data-distinguishedName');
    var nombreCompleto = (nombrePila.trim() + ' ' + apellidos.trim()).trim();
    var nombreProyecto= button.getAttribute('data-proyecto');

    document.getElementById('nombre_usuario').value =nombre ;
    document.getElementById('nombre_pila').value = nombrePila;
    document.getElementById('apellido').value = apellidos;
    document.getElementById('puestoCT').value = puesto;
    document.getElementById('nombre_inicio_sesion').value = nombreSesion;
    document.getElementById('nameProyecto').value =nombreProyecto ;


    document.getElementById('nombre_completo').value =nombreCompleto;
    document.getElementById('email').value = "@grupo-iai.com.mx" ;
    //document.getElementById('departamento').value = departamento ;
    var selectElement = document.getElementById('departamento');
    selectElement.value = departamento; // Cambia el valor como antes
    // Crear y disparar el evento 'change' manualmente
    
    var event = new Event('change', { bubbles: true });
    selectElement.dispatchEvent(event);
    document.getElementById('distinguished_name').value =distinguishedName;


}
document.addEventListener('DOMContentLoaded', function () {
    var nombreUsuarioInput = document.getElementById('nombre_usuario');
    var nombreInicioSesionInput = document.getElementById('nombre_inicio_sesion');
    var correoInput = document.getElementById('email');
    var dominioEmail = "@grupo-iai.com.mx"; // Puedes cambiar esto según sea necesario

    nombreUsuarioInput.addEventListener('input', function () {
        nombreInicioSesionInput.value = nombreUsuarioInput.value;
        correoInput.value = nombreUsuarioInput.value + dominioEmail;
    });
});

document.addEventListener('DOMContentLoaded', function () {
    var nombrePilaInput = document.getElementById('nombre_pila');
    var apellidoInput = document.getElementById('apellido');
    var nombreCompletoInput = document.getElementById('nombre_completo');

    function actualizarNombreCompleto() {
        nombreCompletoInput.value = nombrePilaInput.value + ' ' + apellidoInput.value;
    }

    nombrePilaInput.addEventListener('input', actualizarNombreCompleto);
    apellidoInput.addEventListener('input', actualizarNombreCompleto);
});

document.addEventListener('DOMContentLoaded', function () {
    var form = document.querySelector('form');
    form.onsubmit = function (e) {
        var password = document.getElementById('password').value;
        var confirmPassword = document.getElementById('confirm_password').value;
        
        if (password != confirmPassword) {
            alert('Las contraseñas no coinciden.');
            e.preventDefault();
            return false;
        }
        return true;
    };
});