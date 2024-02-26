$(document).ready(function() {
    var config = {
        "pageLength": 10,
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