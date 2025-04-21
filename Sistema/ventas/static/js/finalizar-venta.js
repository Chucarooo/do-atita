// Archivo independiente para finalizar venta
function finalizarVentaDirecto() {
    console.log("Iniciando finalizarVenta...");
    
    // Verificar que haya productos en el carrito
    const filas = document.querySelectorAll('#tablaCarrito tbody tr');
    console.log("Filas encontradas:", filas.length);
    
    if (filas.length === 0) {
        mostrarErrorEnModal('Debe agregar al menos un producto para realizar la venta');
        return false;
    }
    
    // Verificar que se haya seleccionado un medio de pago principal
    const medioPagoPrincipal = document.getElementById('medio_pago_principal').value;
    console.log("Medio de pago principal:", medioPagoPrincipal);
    
    if (!medioPagoPrincipal) {
        mostrarErrorEnModal('Debe seleccionar un medio de pago principal');
        return false;
    }
    
    // Verificar que el monto principal sea válido
    const montoPrincipal = parseFloat(document.getElementById('monto_principal').value);
    console.log("Monto principal:", montoPrincipal);
    
    if (isNaN(montoPrincipal) || montoPrincipal <= 0) {
        mostrarErrorEnModal('El monto del pago principal debe ser mayor a cero');
        return false;
    }
    
    // Si se usa segundo medio de pago, verificar que sea válido
    const usarSegundoMedio = document.getElementById('usar_segundo_medio').checked;
    console.log("Usar segundo medio:", usarSegundoMedio);
    
    if (usarSegundoMedio) {
        const medioPagoSecundario = document.getElementById('medio_pago_secundario').value;
        const montoSecundario = parseFloat(document.getElementById('monto_secundario').value);
        
        console.log("Medio de pago secundario:", medioPagoSecundario);
        console.log("Monto secundario:", montoSecundario);
        
        if (!medioPagoSecundario) {
            mostrarErrorEnModal('Debe seleccionar un medio de pago secundario');
            return false;
        }
        
        if (isNaN(montoSecundario) || montoSecundario <= 0) {
            mostrarErrorEnModal('El monto del pago secundario debe ser mayor a cero');
            return false;
        }
    }
    
    // Verificar que el total de los pagos sea igual al total de la venta
    const totalVenta = parseFloat(document.getElementById('totalVenta').textContent.replace('$', ''));
    console.log("Total venta:", totalVenta);
    
    let totalPagos = montoPrincipal;
    
    if (usarSegundoMedio) {
        totalPagos += parseFloat(document.getElementById('monto_secundario').value);
    }
    
    console.log("Total pagos:", totalPagos);
    
    if (Math.abs(totalVenta - totalPagos) > 0.01) {
        mostrarErrorEnModal('El total de los pagos debe ser igual al total de la venta');
        return false;
    }
    
    // Preparar datos de productos
    const productos = [];
    filas.forEach(function(fila) {
        const productoId = fila.getAttribute('data-id');
        const cantidad = fila.querySelector('.cantidad-producto').value;
        const precio = fila.querySelector('.precio-unitario').textContent.replace('$', '');
        
        console.log("Producto encontrado:", {
            id: productoId,
            cantidad: cantidad,
            precio: precio
        });
        
        productos.push({
            id: productoId,
            cantidad: cantidad,
            precio: precio
        });
    });
    
    console.log("Productos a enviar:", productos);
    
    // Preparar datos para enviar
    const formData = new FormData();
    formData.append('productos', JSON.stringify(productos));
    formData.append('medio_pago_principal', medioPagoPrincipal);
    formData.append('monto_principal', montoPrincipal);
    
    if (usarSegundoMedio) {
        formData.append('medio_pago_secundario', document.getElementById('medio_pago_secundario').value);
        formData.append('monto_secundario', document.getElementById('monto_secundario').value);
    }
    
    // Mostrar contenido del FormData
    console.log("Datos a enviar:");
    for (let pair of formData.entries()) {
        console.log(pair[0] + ': ' + pair[1]);
    }
    
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
        if (data.success) {
            // Mostrar mensaje de éxito
            mostrarExitoEnModal(data.venta_id);
            // Limpiar el carrito y recargar la página después de 2 segundos
            setTimeout(() => {
                window.location.href = window.location.pathname;
            }, 2000);
        } else {
            // Mostrar mensaje de error
            mostrarErrorEnModal(data.error);
        }
    })
    .catch(error => {
        console.error("Error en la venta:", error);
        mostrarErrorEnModal('Error al procesar la venta');
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
