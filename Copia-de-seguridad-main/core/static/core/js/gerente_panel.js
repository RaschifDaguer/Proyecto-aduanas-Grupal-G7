// core/static/core/js/gerente_panel.js
// Panel Gerente: Autocompletado, CRUD y tablas dinámicas para empleados y aranceles
// Requiere jQuery y Bootstrap 5

$(document).ready(function() {
    // --- Empleados ---
    cargarTablaEmpleados();
    $("#buscador-empleados").on("input focus", function() {
        let q = $(this).val();
        // Mostrar todos si está vacío
        $.get('/core/ajax/buscar_empleados/', {q: q}, function(data) {
            mostrarSugerencias('#sugerencias-empleados', data, 'empleado');
        });
    });
    $(document).on('click', '.sugerencia-empleado', function() {
        let id = $(this).data('id');
        cargarTablaEmpleados(id);
        $('#buscador-empleados').val($(this).text());
        $('#sugerencias-empleados').empty();
    });
    $('#btn-add-empleado').click(function() {
        abrirModalEmpleado('add');
    });
    $(document).on('click', '.btn-edit-empleado', function() {
        abrirModalEmpleado('edit', $(this).data('id'));
    });
    $(document).on('click', '.btn-delete-empleado', function() {
        abrirModalEmpleado('delete', $(this).data('id'));
    });

    // --- Aranceles ---
    cargarTablaAranceles();
    $("#buscador-aranceles").on("input focus", function() {
        let q = $(this).val();
        // Mostrar todos si está vacío
        $.get('/core/ajax/buscar_aranceles/', {q: q}, function(data) {
            mostrarSugerencias('#sugerencias-aranceles', data, 'arancel');
        });
    });
    $(document).on('click', '.sugerencia-arancel', function() {
        let id = $(this).data('id');
        cargarTablaAranceles(id);
        $('#buscador-aranceles').val($(this).text());
        $('#sugerencias-aranceles').empty();
    });
    $('#btn-add-arancel').click(function() {
        abrirModalArancel('add');
    });
    $(document).on('click', '.btn-edit-arancel', function() {
        abrirModalArancel('edit', $(this).data('id'));
    });
    $(document).on('click', '.btn-delete-arancel', function() {
        abrirModalArancel('delete', $(this).data('id'));
    });

    // --- Historial ---
    cargarUsuariosFiltro();
    cargarTablaHistorial();
    $('#filtro-usuario').change(function() {
        cargarTablaHistorial($(this).val());
    });

    // --- Buscador visual sobre la tabla de aranceles ---
    $('#buscador-aranceles-tabla').on('input focus', function() {
        let q = $(this).val();
        $.get('/core/ajax/buscar_aranceles/', {q: q}, function(data) {
            let html = '';
            if (data.length === 0) {
                html = '<div class="text-muted px-2 py-1">No hay resultados</div>';
            } else {
                data.forEach(function(item) {
                    html += `<div class=\"sugerencia-arancel-tabla\" data-id=\"${item.id}\">${item.texto}</div>`;
                });
            }
            $('#sugerencias-aranceles-tabla').html(html).show();
        });
    });
    $(document).on('click', '.sugerencia-arancel-tabla', function() {
        let id = $(this).data('id');
        // Scroll y resaltado
        let row = $("#arancel-row-" + id);
        if (row.length) {
            $('.table tr').removeClass('table-warning');
            row.addClass('table-warning');
            $('html, body').animate({ scrollTop: row.offset().top - 120 }, 500);
        }
        $('#sugerencias-aranceles-tabla').empty();
        $('#buscador-aranceles-tabla').val(row.find('td').eq(0).text() + ' - ' + row.find('td').eq(1).text());
    });

    // --- Secciones y Capítulos ---
    $('#add-seccion-btn').click(function() {
        $('#seccionModalLabel').text('Agregar Sección');
        $('#seccion-form-fields').html('<div class="text-center text-muted py-3">Cargando formulario...</div>');
        $.get('/core/ajax/form_seccion/', function(resp) {
            $('#seccion-form-fields').html(resp.html);
            $('#seccionModal').modal('show');
        });
    });
    $('#add-capitulo-btn').click(function() {
        $('#capituloModalLabel').text('Agregar Capítulo');
        $('#capitulo-form-fields').html('<div class="text-center text-muted py-3">Cargando formulario...</div>');
        $.get('/core/ajax/form_capitulo/', function(resp) {
            $('#capitulo-form-fields').html(resp.html);
            $('#capituloModal').modal('show');
        });
    });
    $('#save-seccion-btn').click(function(e) {
        e.preventDefault();
        let form = $('#seccion-form');
        $.post('/core/ajax/form_seccion/', form.serialize(), function(resp) {
            if (resp.success) {
                $('#seccionModal').modal('hide');
                showMessage('Sección agregada correctamente', 'success');
            } else {
                $('#seccion-form-fields').html(resp.html);
            }
        });
    });
    $('#save-capitulo-btn').click(function(e) {
        e.preventDefault();
        let form = $('#capitulo-form');
        $.post('/core/ajax/form_capitulo/', form.serialize(), function(resp) {
            if (resp.success) {
                $('#capituloModal').modal('hide');
                showMessage('Capítulo agregado correctamente', 'success');
            } else {
                $('#capitulo-form-fields').html(resp.html);
            }
        });
    });

    // --- Funciones auxiliares ---
    function mostrarSugerencias(selector, data, tipo) {
        let html = '';
        if (data.length === 0) {
            html = '<div class="text-muted px-2 py-1">No hay resultados</div>';
        } else {
            data.forEach(function(item) {
                html += `<div class="sugerencia-${tipo}" data-id="${item.id}">${item.texto}</div>`;
            });
        }
        $(selector).html(html).show();
    }

    function cargarTablaEmpleados(filtro_id) {
        $.get('/core/ajax/tabla_empleados/', {id: filtro_id}, function(resp) {
            $('#tabla-empleados-container').html(resp.html);
        });
    }
    function abrirModalEmpleado(accion, id) {
        let url = '/core/ajax/form_empleado/';
        if (accion !== 'add') url += id + '/';
        $.get(url, {accion: accion}, function(resp) {
            $('#modal-crud-title').text(accion === 'add' ? 'Agregar Empleado' : accion === 'edit' ? 'Editar Empleado' : 'Eliminar Empleado');
            $('#modal-crud-body').html(resp.html);
            $('#modal-crud').modal('show');
        });
    }
    $('#modal-crud-save').click(function() {
        let form = $('#modal-crud-body form');
        let url = form.attr('action');
        let method = form.attr('method');
        let data = form.serialize();
        $.ajax({url: url, method: method, data: data, success: function(resp) {
            if (resp.success) {
                $('#modal-crud').modal('hide');
                cargarTablaEmpleados();
            } else {
                $('#modal-crud-body').html(resp.html);
            }
        }});
    });

    function cargarTablaAranceles(filtro_id) {
        $.get('/core/ajax/tabla_aranceles/', {id: filtro_id}, function(resp) {
            $('#tabla-aranceles-container').html(resp.html);
        });
    }
    function abrirModalArancel(accion, id) {
        let url = '/core/ajax/form_arancel/';
        if (accion !== 'add') url += id + '/';
        $.get(url, {accion: accion}, function(resp) {
            $('#modal-crud-title').text(accion === 'add' ? 'Agregar Arancel' : accion === 'edit' ? 'Editar Arancel' : 'Eliminar Arancel');
            $('#modal-crud-body').html(resp.html);
            $('#modal-crud').modal('show');
        });
    }
    // Guardar arancel
    // Puedes reutilizar el mismo botón y lógica que empleados
    
    function cargarUsuariosFiltro() {
        $.get('/core/ajax/lista_usuarios/', function(data) {
            let html = '<option value="">Todos</option>';
            data.forEach(function(u) {
                html += `<option value="${u.id}">${u.texto}</option>`;
            });
            $('#filtro-usuario').html(html);
        });
    }
    function cargarTablaHistorial(usuario_id) {
        $.get('/core/ajax/tabla_historial/', {usuario: usuario_id}, function(resp) {
            $('#tabla-historial-container').html(resp.html);
        });
    }
});
