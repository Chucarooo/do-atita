// Variables globales
let totalVenta = 0;
let productosVenta = [];

// Archivo independiente para finalizar venta
function finalizarVentaDirecto() {
    console.log("Iniciando finalizarVenta...");
    
    // Mostrar indicador de carga
    Swal.fire({
        title: 'Procesando venta...',
        allowOutsideClick: false,
        didOpen: () => {
            Swal.showLoading();
        }
    });
    
    // Verificar que haya productos en el carrito
    if (productos.length === 0) {
        Swal.close();
        mostrarErrorEnModal('Debe agregar al menos un producto para realizar la venta');
        return false;
    }
    
    // Verificar que se haya seleccionado un medio de pago
    const medioPago = document.getElementById('medio_pago_principal').value;
    console.log("Medio de pago:", medioPago);
    
    if (!medioPago) {
        Swal.close();
        mostrarErrorEnModal('Debe seleccionar un medio de pago');
        return false;
    }
    
    // Verificar que el monto sea válido
    const monto = parseFloat(document.getElementById('monto_principal').value);
    console.log("Monto:", monto);
    
    if (isNaN(monto) || monto <= 0) {
        Swal.close();
        mostrarErrorEnModal('El monto debe ser mayor a cero');
        return false;
    }
    
    // Verificar que el monto sea igual al total de la venta
    const totalVenta = parseFloat(document.getElementById('totalVenta').textContent.replace('$', ''));
    console.log("Total venta:", totalVenta);
    
    if (Math.abs(totalVenta - monto) > 0.01) {
        Swal.close();
        mostrarErrorEnModal('El monto debe ser igual al total de la venta');
        return false;
    }
    
    // Preparar datos de productos
    const productosEnviar = productos.map(producto => ({
        id: producto.id,
        cantidad: producto.cantidad,
        precio: producto.precioContado
    }));
    
    console.log("Productos a enviar:", productosEnviar);
    
    // Preparar datos para enviar
    const formData = new FormData();
    formData.append('productos', JSON.stringify(productosEnviar));
    formData.append('medio_pago_principal', medioPago);
    formData.append('monto_principal', monto);
    
    // Enviar datos al servidor
    console.log("Preparando datos para enviar...");
    fetch('/ventas/', {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        }
    })
    .then(response => response.json())
    .then(data => {
        console.log("Respuesta del servidor:", data);
        Swal.close();
        if (data.success) {
            mostrarExitoEnModal(data.venta_id);
            // Limpiar el carrito y recargar la página después de 2 segundos
            setTimeout(() => {
                window.location.href = window.location.pathname;
            }, 2000);
        } else {
            mostrarErrorEnModal(data.error || 'Error al procesar la venta');
        }
    })
    .catch(error => {
        console.error("Error en la venta:", error);
        Swal.close();
        mostrarErrorEnModal('Error al comunicarse con el servidor');
    });
    
    return false;
}

// Función para mostrar éxito en el modal
function mostrarExitoEnModal(ventaId) {
    console.log("Mostrando modal de éxito para venta:", ventaId);
    const modalBody = document.getElementById('resultadoVentaModalBody');
    const btnNuevaVenta = document.getElementById('btnNuevaVenta');
    const btnImprimirTicket = document.getElementById('btnImprimirTicket');
    
    modalBody.innerHTML = `
        <div class="text-center">
            <i class="fas fa-check-circle text-success" style="font-size: 64px;"></i>
            <h4 class="mt-3">¡Venta Exitosa!</h4>
            <p class="mt-3">La venta #${ventaId} ha sido registrada correctamente.</p>
        </div>
    `;
    
    // Mostrar los botones cuando hay éxito
    btnNuevaVenta.style.display = 'block';
    btnImprimirTicket.style.display = 'block';
    
    // Configurar el botón de imprimir ticket
    btnImprimirTicket.onclick = function() {
        console.log('Intentando imprimir ticket para venta:', ventaId);
        if (ventaId) {
            const url = `/ventas/imprimir_ticket/${ventaId}/`;
            console.log('URL para imprimir ticket:', url);
            window.open(url, '_blank');
        }
    };
    
    // Mostrar el modal usando jQuery
    $('#resultadoVentaModal').modal({
        backdrop: 'static',
        keyboard: false
    });
}

// Función para mostrar errores en el modal
function mostrarErrorEnModal(mensaje) {
    const modalBody = document.getElementById('resultadoVentaModalBody');
    const btnNuevaVenta = document.getElementById('btnNuevaVenta');
    const btnImprimirTicket = document.getElementById('btnImprimirTicket');
    
    modalBody.innerHTML = `
        <div class="text-center">
            <i class="fas fa-exclamation-circle text-danger" style="font-size: 64px;"></i>
            <h4 class="mt-3">Error</h4>
            <p class="mt-3">${mensaje}</p>
        </div>
    `;
    
    // Ocultar los botones cuando hay error
    btnNuevaVenta.style.display = 'none';
    btnImprimirTicket.style.display = 'none';
    
    $('#resultadoVentaModal').modal('show');
}

// Función para agregar producto al carrito
function agregarProducto(id, nombre, precioLista, precioContado, stock) {
    // Verificar si el producto ya está en el carrito
    const productoExistente = productos.find(p => p.id === id);
    
    if (productoExistente) {
        // Si el producto ya está en el carrito, aumentar la cantidad
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
        // Si no está en el carrito, agregarlo
        productos.push({
            id: id,
            nombre: nombre,
            precioLista: precioLista,
            precioContado: precioContado,
            cantidad: 1,
            stock: stock
        });
    }
    
    // Actualizar el carrito
    actualizarCarrito();
}

// Función para cambiar la cantidad de un producto
function cambiarCantidad(index, delta) {
    const fila = document.querySelectorAll('#tablaCarrito tbody tr')[index];
    const inputCantidad = fila.querySelector('input[type="number"]');
    const nuevaCantidad = parseInt(inputCantidad.value) + delta;
    
    // Obtener el stock del array productos
    const stock = productos[index].stock;
    
    if (nuevaCantidad > 0 && nuevaCantidad <= stock) {
        // Actualizar la cantidad en el array productos
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

// Función para actualizar la cantidad de un producto
function actualizarCantidad(index, nuevaCantidad) {
    const fila = document.querySelectorAll('#tablaCarrito tbody tr')[index];
    
    // Obtener el precio del array productos
    const precio = productos[index].precioContado;
    const subtotal = precio * nuevaCantidad;
    
    // Actualizar el subtotal en la tabla
    const celdaSubtotal = fila.querySelector('td:nth-child(4)');
    celdaSubtotal.textContent = `$${subtotal.toFixed(2)}`;
    
    // Actualizar el total general
    let total = 0;
    productos.forEach(producto => {
        total += producto.precioContado * producto.cantidad;
    });
    
    document.getElementById('totalVenta').textContent = `$${total.toFixed(2)}`;
    document.getElementById('monto_principal').value = total.toFixed(2);
}

// Función para eliminar un producto del carrito
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
            // Eliminar el producto del array
            productos.splice(index, 1);
            
            // Actualizar el carrito completo
            actualizarCarrito();
            
            // Mostrar mensaje de éxito
            Swal.fire({
                title: '¡Eliminado!',
                text: 'El producto ha sido eliminado del carrito',
                icon: 'success',
                timer: 1500,
                showConfirmButton: false
            });
        }
    }).catch(() => {
        // En caso de error en el modal
        console.log('Error en el modal de confirmación');
    });
}

// Función para actualizar el carrito
function actualizarCarrito() {
    const tbody = $('#tablaCarrito tbody');
    tbody.empty();
    
    totalVenta = 0;
    
    productos.forEach((producto, index) => {
        const subtotal = producto.cantidad * producto.precioContado;
        totalVenta += subtotal;
        
        const fila = $(`
            <tr data-id="${producto.id}" 
                data-precio-lista="${producto.precioLista}" 
                data-precio-contado="${producto.precioContado}"
                data-stock="${producto.stock}">
                <td>${producto.nombre}</td>
                <td class="text-center">
                    <div class="input-group input-group-sm">
                        <button class="btn btn-outline-secondary" type="button" onclick="cambiarCantidad(${index}, -1)">-</button>
                        <input type="number" class="form-control text-center" value="${producto.cantidad}" 
                               min="1" max="${producto.stock}" onchange="actualizarCantidad(${index}, this.value)">
                        <button class="btn btn-outline-secondary" type="button" onclick="cambiarCantidad(${index}, 1)">+</button>
                    </div>
                </td>
                <td class="text-end">$${producto.precioContado.toFixed(2)}</td>
                <td class="text-end">$${subtotal.toFixed(2)}</td>
                <td class="text-center">
                    <button class="btn btn-danger btn-sm" onclick="eliminarProducto(${index})">
                        <i class="fas fa-trash"></i>
                    </button>
                </td>
            </tr>
        `);
        
        tbody.append(fila);
    });
    
    // Actualizar el total
    $('#totalVenta').text(`$${totalVenta.toFixed(2)}`);
    
    // Actualizar el monto principal con el total
    $('#monto_principal').val(totalVenta.toFixed(2));
    
    // Habilitar/deshabilitar el botón de finalizar venta
    const btnFinalizar = $('#btnFinalizarVenta');
    const habilitado = productos.length > 0;
    btnFinalizar.prop('disabled', !habilitado);
    
    // Si no hay productos, limpiar el monto principal
    if (!habilitado) {
        $('#monto_principal').val('0.00');
    }
    
    // Agregar evento click al botón de finalizar si está habilitado
    if (habilitado) {
        btnFinalizar.off('click').on('click', function() {
            finalizarVenta();
        });
    }
}

// Función para finalizar la venta
function finalizarVenta() {
    console.log('Iniciando finalizarVenta...');
    
    // Verificar que haya productos en el carrito
    if (productos.length === 0) {
        Swal.fire({
            icon: 'warning',
            title: 'Carrito vacío',
            text: 'Debe agregar al menos un producto para realizar la venta'
        });
        return;
    }
    
    if (typeof finalizarVentaDirecto === 'function') {
        finalizarVentaDirecto();
    } else {
        console.error('La función finalizarVentaDirecto no está definida');
        Swal.fire({
            icon: 'error',
            title: 'Error',
            text: 'Error al procesar la venta. Por favor, recargue la página.'
        });
    }
}
