function addDomainIfEmpty(inputElement) {
    var nombreUsuarioInput = document.getElementById('nombre_usuario');

    if (inputElement.value.trim() === "") {
        inputElement.value = nombreUsuarioInput.value +"@grupo-iai.com.mx";
    }
}


document.addEventListener('DOMContentLoaded', function () {

   
    var form = document.getElementById('miFormulario2');
    form.onsubmit = function (e) {
        var password = document.getElementById('password').value;
        var confirmPassword = document.getElementById('confirm_password').value;
        let botonGuardar = document.getElementById('botonGuardar');
        console.log(password );
        if (password != confirmPassword) {
           // alert('Las contraseñas no coinciden.');
           document.getElementById('confirm_password').value="";
           document.getElementById('password').value="";
            Swal.fire({
                title: "¡Las contraseñas no coincide.!",
                text: ". . .",
                icon: "warning",  // 'success', 'error', 'warning', 'info', 'question'
                confirmButtonText: 'Ok'
            });
            e.preventDefault();
            
            botonGuardar.disabled = false; // Deshabilita el botón para prevenir múltiples envíos
            botonGuardar.textContent = 'Guardar'; // Opcional: Cambia el texto para indicar que se está procesando
            return false;
        }
        mostrarSpinner()
        botonGuardar.disabled = true; // Deshabilita el botón para prevenir múltiples envíos
        botonGuardar.textContent = 'Guardando...'; // Opcional: Cambia el texto para indicar que se está procesando
        return true;
    };
});







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

    document.getElementById('nombre_usuario').value =generadorNombreUsuario() ;
    document.getElementById('nombre_pila').value = nombrePila;
    document.getElementById('apellido').value = apellidos;
    document.getElementById('puestoCT').value = puesto;
    document.getElementById('nombre_inicio_sesion').value = generadorNombreUsuario();
    document.getElementById('nameProyecto').value =nombreProyecto ;
    //console.log(nombre)
   // console.log(nombreSesion)
    document.getElementById('confirm_password').value="";
    document.getElementById('password').value="";
    document.getElementById('nombre_completo').value =nombreCompleto;
    document.getElementById('email').value = generadorNombreUsuario()+"@grupo-iai.com.mx" ;
    //document.getElementById('departamento').value = departamento ;
    var selectElement = document.getElementById('departamento');
    selectElement.value = departamento; // Cambia el valor como antes
    // Crear y disparar el evento 'change' manualmente
    
    var event = new Event('change', { bubbles: true });
    selectElement.dispatchEvent(event);
    document.getElementById('distinguished_name').value =distinguishedName;
    validarnuevoUsuario()

}

function generadorNombreUsuario(){
    
    // Si necesitas obtener estos valores de otros elementos input, deberías hacerlo así:
    var nombrePila = document.getElementById('nombre_pila').value;
    var apellidos = document.getElementById('apellido').value;

    // Extrae la primera palabra de nombrePila y apellidos
    var primeraPalabraNombrePila = nombrePila.split(' ')[0];
    var primeraPalabraApellido = apellidos.split(' ')[0];

    // Combina las primeras palabras
    let nombreUsuario = primeraPalabraNombrePila + "." + primeraPalabraApellido;
    
    




    return nombreUsuario 
}


function validarnuevoUsuario(){
    var nombre2 = document.getElementById('nombre_inicio_sesion').value;
    document.getElementById('nombre_usuario').value =nombre2 
    verificarUsuario(nombre2);
}

function verificarUsuario(nombreUsuario) {
    mostrarSpinner()
    document.getElementById('botonGuardar').disabled = true;
    fetch(`/verificar-usuario/${nombreUsuario}/`)
    .then(response => response.json())
    .then(data => {
        let botonGuardar = document.getElementById('botonGuardar');
        
        if (data.existe) {
            botonGuardar.disabled = true;
            botonGuardar.innerText = "Usuario Existente"; // Cambia el texto
            botonGuardar.classList.add('btn-danger');
            botonGuardar.classList.remove('btn-primary');
            ocultarSpinner() 
            mensaje('¡Usuario existe  !','en Active Directory.','warning');
         
        } else {
            ocultarSpinner() 
           

            mensaje('¡Usuario No existe !','en Active Directory.','success');
            botonGuardar.disabled = false;
            botonGuardar.innerText = "Guardar"; // Restablece el texto original o elige uno nuevo
            botonGuardar.classList.add('btn-primary');
            botonGuardar.classList.remove('btn-danger');
            
        }
    })
    
    .catch(error => console.error('Error:', error));
    }


    
    function mensaje (ti,te,ico) {
        Swal.fire({
            title: ti,
            text: te,
            icon: ico
        });
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



     