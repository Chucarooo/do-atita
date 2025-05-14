// Variables globales
let productos = [];
let total = 0;
let totalVenta = 0;
let productosVenta = [];

// =============================================
// INICIALIZACIÓN Y CONFIGURACIÓN
// =============================================

// Cuando el documento esté listo
document.addEventListener('DOMContentLoaded', function() {
    // Establecer el foco en el campo de búsqueda
    $('#buscarProducto').focus();
    
    // Establecer la fecha actual
    const fechaActual = new Date().toISOString().split('T')[0];
    $('#fecha_comprobante').val(fechaActual);
    
    // Inicializar los productos
    inicializarProductos();
    
    // Configurar eventos
    configurarEventos();
    
    // Configurar AJAX
    configurarAjax();
});

// Función para inicializar productos
function inicializarProductos() {
    $('.list-group-item').each(function() {
        const btnAgregar = $(this).find('.btn-agregar');
        const id = btnAgregar.data('id');
        const nombre = $(this).find('.col-3').text();
        const precioLista = parseFloat(btnAgregar.data('precio-lista'));
        const precioContado = parseFloat(btnAgregar.data('precio-contado'));
        const stock = parseInt(btnAgregar.data('stock'));
        const codigoBarras = btnAgregar.data('codigo-barras');
        
        $(this).data('codigo-barras', codigoBarras);
    });
}

// Función para configurar eventos
function configurarEventos() {
    // Evento para el campo de búsqueda
    $('#buscarProducto').on('input', filtrarProductos);
    
    // Evento para detectar cuando se presiona Enter en el campo de búsqueda
    $('#buscarProducto').on('keypress', function(e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            const valor = $(this).val().trim();
            
            if (/^\d+$/.test(valor) && valor.length >= 8) {
                manejarLecturaCodigoBarras(valor);
            }
        }
    });

    // Remover eventos anteriores y agregar nuevo evento click a los botones de agregar
    $(document).off('click', '.btn-agregar').on('click', '.btn-agregar', function(e) {
        e.preventDefault();
        const id = $(this).data('id');
        const nombre = $(this).data('nombre');
        const precioLista = parseFloat($(this).data('precio-lista'));
        const precioContado = parseFloat($(this).data('precio-contado'));
        const stock = parseInt($(this).data('stock'));
        
        agregarProducto(id, nombre, precioLista, precioContado, stock);
    });

    // Evento para el formulario de marca
    $('#addMarcaForm').on('submit', manejarAgregarMarca);
}

// Función para configurar AJAX
function configurarAjax() {
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", $('input[name=csrfmiddlewaretoken]').val());
            }
            }
        });
    }

// =============================================
// FUNCIONES DE BÚSQUEDA Y FILTRADO
// =============================================

// Función para filtrar productos
function filtrarProductos() {
    const texto = $('#buscarProducto').val().toLowerCase();
    const items = $('.list-group-item');
    
    if (!texto) {
        items.hide();
        return;
    }
    
    if (/^\d+$/.test(texto) && texto.length >= 8) {
        items.hide();
        } else {
        items.each(function() {
            const nombre = $(this).find('.col-3').text().toLowerCase();
            $(this).toggle(nombre.includes(texto));
        });
    }
}

// Función para buscar producto por código de barras
function buscarProductoPorCodigoBarras(codigo) {
    let productoEncontrado = null;
    const codigoBuscado = codigo.toString();
    
    $('.list-group-item').each(function() {
        const btnAgregar = $(this).find('.btn-agregar');
        const codigoBarras = btnAgregar.data('codigo-barras');
        const codigoProducto = codigoBarras ? codigoBarras.toString() : null;
        
        if (codigoProducto === codigoBuscado) {
            productoEncontrado = {
                id: btnAgregar.data('id'),
                nombre: btnAgregar.data('nombre'),
                precioLista: parseFloat(btnAgregar.data('precio-lista')),
                precioContado: parseFloat(btnAgregar.data('precio-contado')),
                stock: parseInt(btnAgregar.data('stock'))
            };
            return false;
        }
    });
    
    return productoEncontrado;
}

// Función para manejar la lectura del código de barras
function manejarLecturaCodigoBarras(codigo) {
    const codigoStr = codigo.toString();
    const producto = buscarProductoPorCodigoBarras(codigoStr);
    
    if (producto) {
        agregarProducto(
            producto.id,
            producto.nombre,
            producto.precioLista,
            producto.precioContado,
            producto.stock
        );
        $('#buscarProducto').val('');
        $('.list-group-item').hide();
    } else {
        Swal.fire({
            icon: 'warning',
            title: 'Producto no encontrado',
            text: 'No se encontró ningún producto con el código de barras escaneado'
        });
        $('#buscarProducto').val('');
    }
}

// =============================================
// FUNCIONES DEL CARRITO
// =============================================

// Función para agregar producto
function agregarProducto(id, nombre, precioLista, precioContado, stock) {
    // Convertir los parámetros a sus tipos correctos
    id = parseInt(id);
    precioLista = typeof precioLista === 'string' 
        ? parseFloat(precioLista.replace(',', '.').replace(/[^0-9.-]+/g, ''))
        : Number(precioLista);
    precioContado = typeof precioContado === 'string'
        ? parseFloat(precioContado.replace(',', '.').replace(/[^0-9.-]+/g, ''))
        : Number(precioContado);
    stock = typeof stock === 'string'
        ? parseInt(stock.replace(/[^0-9]+/g, ''))
        : Number(stock);
    
    // Verificar si ya existe en el carrito
    const productoExistente = productos.find(p => p.id === id);
    
    if (productoExistente) {
        if (productoExistente.cantidad < stock) {
            productoExistente.cantidad++;
        } else {
            Swal.fire({
                icon: 'warning',
                title: 'Stock insuficiente',
                text: `No hay suficiente stock disponible. Stock actual: ${stock}`
            });
            return;
        }
    } else {
        productos.push({
            id: id,
            nombre: nombre,
            precioLista: precioLista,
            precioContado: precioContado,
            cantidad: 1,
            stock: stock
        });
    }
    
    actualizarCarrito();
}

// Función para actualizar el carrito
function actualizarCarrito() {
    const tbody = $('#tablaCarrito tbody');
    tbody.empty();
    
    total = 0;
    
    productos.forEach((producto, index) => {
        const subtotal = producto.cantidad * producto.precioContado;
        total += subtotal;
        
        // Crear la fila con jQuery para mejor manejo de eventos
        const fila = $(`
            <tr>
                <td>${producto.nombre}</td>
                <td class="text-center">
                    <div class="input-group input-group-sm">
                        <button class="btn btn-outline-secondary btn-decrementar" type="button">-</button>
                        <input type="number" class="form-control text-center input-cantidad" value="${producto.cantidad}" 
                               min="1" max="${producto.stock}">
                        <button class="btn btn-outline-secondary btn-incrementar" type="button">+</button>
                    </div>
                </td>
                <td class="text-end">$${producto.precioContado.toFixed(2)}</td>
                <td class="text-end">$${subtotal.toFixed(2)}</td>
                <td class="text-center">
                    <button class="btn btn-danger btn-sm btn-eliminar">
                        <i class="fas fa-trash"></i>
                    </button>
                </td>
            </tr>
        `);
        
        // Agregar event listeners a los botones
        fila.find('.btn-decrementar').on('click', function() {
            cambiarCantidad(index, -1);
        });
        
        fila.find('.btn-incrementar').on('click', function() {
            cambiarCantidad(index, 1);
        });
        
        fila.find('.input-cantidad').on('change', function() {
            actualizarCantidad(index, parseInt(this.value));
        });
        
        fila.find('.btn-eliminar').on('click', function() {
            eliminarProducto(index);
        });
        
        tbody.append(fila);
    });
    
    // Actualizar el total
    $('#totalVenta').text(`$${total.toFixed(2)}`);
    
    // Actualizar el monto principal con el total
    $('#monto_principal').val(total.toFixed(2));
    
    // Habilitar/deshabilitar el botón de finalizar venta
    const btnFinalizar = $('#btnFinalizarVenta');
    const habilitado = productos.length > 0;
    btnFinalizar.prop('disabled', !habilitado);
    
    // Agregar evento click al botón de finalizar si está habilitado
    if (habilitado) {
        btnFinalizar.off('click').on('click', finalizarVenta);
    }
}

// Función para cambiar cantidad
function cambiarCantidad(index, delta) {
    if (index < 0 || index >= productos.length) {
        return;
    }
    
    const fila = document.querySelectorAll('#tablaCarrito tbody tr')[index];
    if (!fila) {
        return;
    }
    
    const inputCantidad = fila.querySelector('input[type="number"]');
    if (!inputCantidad) {
        return;
    }
    
    const nuevaCantidad = parseInt(inputCantidad.value) + delta;
    const stock = productos[index].stock;
    
    if (nuevaCantidad > 0 && nuevaCantidad <= stock) {
        productos[index].cantidad = nuevaCantidad;
        inputCantidad.value = nuevaCantidad;
        actualizarCantidad(index, nuevaCantidad);
    } else if (nuevaCantidad > stock) {
        Swal.fire({
            icon: 'warning',
            title: 'Stock insuficiente',
            text: `No hay suficiente stock disponible. Stock actual: ${stock}`,
            timer: 2000,
            showConfirmButton: false
        });
    }
}

// Función para actualizar cantidad
function actualizarCantidad(index, nuevaCantidad) {
    const fila = document.querySelectorAll('#tablaCarrito tbody tr')[index];
    const precio = productos[index].precioContado;
    const subtotal = precio * nuevaCantidad;
    
    const celdaSubtotal = fila.querySelector('td:nth-child(4)');
    celdaSubtotal.textContent = `$${subtotal.toFixed(2)}`;
    
    let total = 0;
    productos.forEach(producto => {
        total += producto.precioContado * producto.cantidad;
    });
    
    $('#totalVenta').text(`$${total.toFixed(2)}`);
    $('#monto_principal').val(total.toFixed(2));
}

// Función para eliminar producto
function eliminarProducto(index) {
    Swal.fire({
        title: '¿Estás seguro?',
        text: "Esta acción no se puede deshacer",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#3085d6',
        cancelButtonColor: '#d33',
        confirmButtonText: 'Sí, eliminar',
        cancelButtonText: 'Cancelar',
        allowOutsideClick: false,
        allowEscapeKey: false
    }).then((result) => {
        if (result.isConfirmed) {
            productos.splice(index, 1);
            actualizarCarrito();
            Swal.fire({
                title: '¡Eliminado!',
                text: 'El producto ha sido eliminado del carrito',
                icon: 'success',
                timer: 1500,
                showConfirmButton: false
            });
        }
    });
}

// =============================================
// FUNCIONES DE VENTA
// =============================================

// Función para finalizar venta
function finalizarVenta() {
    Swal.fire({
        title: 'Procesando venta...',
        allowOutsideClick: false,
        didOpen: () => {
            Swal.showLoading();
        }
    });
    
    if (productos.length === 0) {
        Swal.close();
        mostrarErrorEnModal('Debe agregar al menos un producto para realizar la venta');
        return false;
    }
    
    const medioPago = $('#medio_pago_principal').val();
    if (!medioPago) {
        Swal.close();
        mostrarErrorEnModal('Debe seleccionar un medio de pago');
        return false;
    }
    
    const monto = parseFloat($('#monto_principal').val());
    if (isNaN(monto) || monto <= 0) {
        Swal.close();
        mostrarErrorEnModal('El monto debe ser mayor a cero');
        return false;
    }
    
    const totalVenta = parseFloat($('#totalVenta').text().replace('$', ''));
    if (Math.abs(totalVenta - monto) > 0.01) {
        Swal.close();
        mostrarErrorEnModal('El monto debe ser igual al total de la venta');
        return false;
    }
    
    const productosEnviar = productos.map(producto => ({
        id: producto.id,
        cantidad: producto.cantidad,
        precio: producto.precioContado
    }));
    
    const formData = new FormData();
    formData.append('productos', JSON.stringify(productosEnviar));
    formData.append('medio_pago_principal', medioPago);
    formData.append('monto_principal', monto);
    
    fetch('/ventas/', {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        }
    })
    .then(response => response.json())
    .then(data => {
        Swal.close();
        if (data.success) {
            mostrarExitoEnModal(data.venta_id);
        } else {
            mostrarErrorEnModal(data.error || 'Error al procesar la venta');
        }
    })
    .catch(error => {
        Swal.close();
        mostrarErrorEnModal('Error al comunicarse con el servidor');
    });
    
    return false;
}

// Función para nueva venta
function nuevaVenta() {
    // Limpiar el carrito
    productos = [];
    total = 0;
    actualizarCarrito();
    
    // Cerrar el modal
    $('#resultadoVentaModal').modal('hide');
    
    // Limpiar campos
    $('#cliente_id').val('');
    $('#fecha_comprobante').val(new Date().toISOString().split('T')[0]);
    $('#medio_pago_principal').val('');
    $('#monto_principal').val('');
    
    // Recargar la página para obtener un nuevo número de comprobante
    window.location.href = window.location.pathname;
}

// =============================================
// FUNCIONES DE MODALES Y NOTIFICACIONES
// =============================================

// Función para mostrar éxito en el modal
function mostrarExitoEnModal(ventaId) {
    const modalBody = $('#resultadoVentaModalBody');
    const btnNuevaVenta = $('#btnNuevaVenta');
    const btnImprimirTicket = $('#btnImprimirTicket');
    
    modalBody.html(`
        <div class="text-center">
            <i class="fas fa-check-circle text-success" style="font-size: 64px;"></i>
            <h4 class="mt-3">¡Venta Exitosa!</h4>
            <p class="mt-3">La venta #${ventaId} ha sido registrada correctamente.</p>
        </div>
    `);
    
    btnNuevaVenta.show();
    btnImprimirTicket.show();
    
    btnImprimirTicket.off('click').on('click', function() {
        if (ventaId) {
            const url = `/ventas/imprimir_ticket/${ventaId}/`;
            const printWindow = window.open(url, '_blank', 'width=400,height=600');
            if (!printWindow) {
                Swal.fire({
                    title: '¡Atención!',
                    text: 'Por favor, permite las ventanas emergentes para imprimir el ticket.',
                    icon: 'warning',
                    confirmButtonText: 'Entendido'
                });
            }
        }
    });
    
    $('#resultadoVentaModal').modal({
        backdrop: 'static',
        keyboard: false
    });
}

// Función para mostrar errores en el modal
function mostrarErrorEnModal(mensaje) {
    const modalBody = $('#resultadoVentaModalBody');
    const btnNuevaVenta = $('#btnNuevaVenta');
    const btnImprimirTicket = $('#btnImprimirTicket');
    
    modalBody.html(`
        <div class="text-center">
            <i class="fas fa-exclamation-circle text-danger" style="font-size: 64px;"></i>
            <h4 class="mt-3">Error</h4>
            <p class="mt-3">${mensaje}</p>
        </div>
    `);
    
    btnNuevaVenta.hide();
    btnImprimirTicket.hide();
    
    $('#resultadoVentaModal').modal('show');
}

// =============================================
// FUNCIONES DE MARCAS
// =============================================

// Función para manejar agregar marca
function manejarAgregarMarca(e) {
    e.preventDefault();
    const nombreMarca = $('#nombreMarca').val().trim();
    
    $.ajax({
        url: '/ventas/verificar_marca/',
        type: 'POST',
        data: {
            'nombre': nombreMarca,
            'csrfmiddlewaretoken': $('input[name=csrfmiddlewaretoken]').val()
        },
        success: function(response) {
            if (response.existe) {
                Swal.fire({
                    icon: 'warning',
                    title: 'Marca existente',
                    text: 'Esta marca ya existe en el sistema.'
                });
                return;
            }
            
            $.ajax({
                url: '/ventas/add_marca/',
                type: 'POST',
                data: {
                    'nombre': nombreMarca,
                    'csrfmiddlewaretoken': $('input[name=csrfmiddlewaretoken]').val()
                },
                success: function(response) {
                    if (response.success) {
                        $('#addMarcaModal').modal('hide');
                        location.reload();
                    } else {
                        Swal.fire({
                            icon: 'error',
                            title: 'Error',
                            text: 'Error al agregar la marca: ' + response.error
                        });
                    }
                },
                error: function() {
                    Swal.fire({
                        icon: 'error',
                        title: 'Error',
                        text: 'Error al comunicarse con el servidor'
                    });
                }
            });
        },
        error: function() {
            Swal.fire({
                icon: 'error',
                title: 'Error',
                text: 'Error al verificar la marca'
            });
        }
    });
}
