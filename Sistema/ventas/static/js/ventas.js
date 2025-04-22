// Variables globales
let productos = [];
let total = 0;

// Cuando el documento esté listo
document.addEventListener('DOMContentLoaded', function() {
   
    
    // Filtrar productos
    
    const inputBusqueda = document.getElementById('buscarProducto');
    if (inputBusqueda) {
        
        inputBusqueda.focus();
        inputBusqueda.addEventListener('keyup', filtrarProductos);
    }
    
    // Agregar productos al carrito
    const botonesAgregar = document.querySelectorAll('.btn-agregar');
    botonesAgregar.forEach(function(boton) {
        boton.addEventListener('click', function(e) {
            e.preventDefault(); // Evitar que el enlace se siga
            const id = parseInt(this.dataset.id);
            const nombre = this.dataset.nombre;
            const precioLista = parseFloat(this.dataset.precioLista);
            const precioContado = parseFloat(this.dataset.precioContado);
            const stock = parseInt(this.dataset.stock);
            
            agregarProducto(id, nombre, precioLista, precioContado, stock);
        });
    });
    
    // Finalizar venta
    const btnFinalizar = document.getElementById('btnFinalizarVenta');
    if (btnFinalizar) {
        btnFinalizar.addEventListener('click', finalizarVenta);
    }
    
    // Establecer la fecha actual en el campo de fecha
    const today = new Date();
    const formattedDate = today.toISOString().substr(0, 10);
    const fechaComprobante = document.getElementById('fecha_comprobante');
    if (fechaComprobante) {
        fechaComprobante.value = formattedDate;
    }
    
    // Manejar el guardado de nuevo cliente
    const btnGuardarCliente = document.getElementById('btnGuardarCliente');
    if (btnGuardarCliente) {
        btnGuardarCliente.addEventListener('click', guardarNuevoCliente);
    }
    
    // Delegación de eventos para los botones de la tabla
    const tablaCarrito = document.querySelector('#tablaCarrito tbody');
    if (tablaCarrito) {
        tablaCarrito.addEventListener('click', function(e) {
            // Si se hizo clic en un botón de eliminar
            if (e.target.closest('.btn-danger')) {
                const row = e.target.closest('tr');
                const index = Array.from(row.parentNode.children).indexOf(row);
                eliminarProductoCarrito(index);
            }
            
            // Si se hizo clic en un botón de disminuir cantidad
            if (e.target.closest('.btn-secondary') && e.target.textContent === '-') {
                const row = e.target.closest('tr');
                const index = Array.from(row.parentNode.children).indexOf(row);
                modificarCantidad(index, -1);
            }
            
            // Si se hizo clic en un botón de aumentar cantidad
            if (e.target.closest('.btn-secondary') && e.target.textContent === '+') {
                const row = e.target.closest('tr');
                const index = Array.from(row.parentNode.children).indexOf(row);
                modificarCantidad(index, 1);
            }
        });
        
        // Delegación de eventos para los inputs de la tabla
        tablaCarrito.addEventListener('change', function(e) {
            // Si se cambió un input de cantidad
            if (e.target.matches('input[type="number"]') && e.target.closest('td').classList.contains('text-center')) {
                const row = e.target.closest('tr');
                const index = Array.from(row.parentNode.children).indexOf(row);
                actualizarCantidadManual(e.target, index);
            }
            
            // Si se cambió un input de precio
            if (e.target.matches('input[type="number"]') && !e.target.closest('td').classList.contains('text-center')) {
                const row = e.target.closest('tr');
                const index = Array.from(row.parentNode.children).indexOf(row);
                actualizarPrecio(e.target, index);
            }
        });
    }
});

// Función para filtrar productos
function filtrarProductos() {
    const texto = document.getElementById('buscarProducto').value.toLowerCase();
    const items = document.querySelectorAll('#lista-productos .list-group-item');
    
    // Si el campo de búsqueda está vacío, ocultar todos los elementos
    if (texto === '') {
        items.forEach(function(item) {
            item.style.display = 'none';
        });
        return;
    }
    
    // Si hay texto, mostrar solo los elementos que coincidan
    items.forEach(function(item) {
        const contenido = item.textContent.toLowerCase();
        if (contenido.includes(texto)) {
            item.style.display = '';
        } else {
            item.style.display = 'none';
        }
    });
}

// Función para agregar producto
function agregarProducto(id, nombre, precioLista, precioContado, stock) {
    // Verificar si ya existe en el carrito
    let existe = false;
    
    for (let i = 0; i < productos.length; i++) {
        if (productos[i].id === id) {
            existe = true;
            if (productos[i].cantidad < stock) {
                productos[i].cantidad++;
                productos[i].subtotal = productos[i].cantidad * productos[i].precioActual;
            } else {
                alert('No hay suficiente stock disponible');
            }
            break;
        }
    }
    
    if (!existe) {
        productos.push({
            id: id,
            nombre: nombre,
            precioLista: precioLista,
            precioContado: precioContado,
            precioActual: precioContado, // Por defecto usamos precio contado
            usandoPrecioContado: true,   // Flag para saber qué precio estamos usando
            cantidad: 1,
            subtotal: precioContado,
            stock: stock  // Agregamos el stock al objeto del producto
        });
    }
    
    actualizarCarrito();
}

// Actualizar carrito
function actualizarCarrito() {
    let html = '';
    let inputsHidden = '';
    total = 0;
    
    for (let i = 0; i < productos.length; i++) {
        let item = productos[i];
        
        // Calcular el subtotal actualizado
        item.subtotal = item.cantidad * item.precioActual;
        total += item.subtotal;
        
        // Determinar qué clase usar para el botón según el precio actual
        let btnClass = item.usandoPrecioContado ? "btn-success" : "btn-warning";
        
        html += `
            <tr data-index="${i}">
                <td>${item.nombre}</td>
                <td class="text-center">
                    <div class="d-flex align-items-center justify-content-center">
                        <button type="button" class="btn btn-sm btn-secondary btn-decrease" onclick="modificarCantidad(${i}, -1)">-</button>
                        <input type="number" value="${item.cantidad}" min="1" class="form-control form-control-sm text-center mx-1" style="width: 60px;" onchange="actualizarCantidadManual(this, ${i})">
                        <button type="button" class="btn btn-sm btn-secondary btn-increase" onclick="modificarCantidad(${i}, 1)">+</button>
                    </div>
                </td>
                <td><input type="number" value="${item.precioActual.toFixed(2)}" min="0" step="0.01" class="form-control form-control-sm" onchange="actualizarPrecio(this, ${i})"></td>
                <td>$${item.subtotal.toFixed(2)}</td>
                <td class="text-center">
                    <div class="d-flex justify-content-center gap-2">
                        <button type="button" class="${btnClass}" style="width: 32px; height: 32px;" onclick="alternarPrecio(${i})">
                            <i class="fas fa-dollar-sign"></i>
                        </button>
                        <button type="button" class="btn btn-danger" style="width: 32px; height: 32px;" onclick="eliminarProductoCarrito(${i})">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </td>
            </tr>
        `;
        
        inputsHidden += `
            <input type="hidden" name="productos_ids" value="${item.id}">
            <input type="hidden" name="cantidades" value="${item.cantidad}">
            <input type="hidden" name="precios" value="${item.precioActual}">
        `;
    }
    
    const tbody = document.querySelector('#tablaCarrito tbody');
    if (tbody) {
        tbody.innerHTML = html;
    }
    
    // Actualizar el total
    const totalVenta = document.getElementById('totalVenta');
    if (totalVenta) {
        totalVenta.textContent = '$' + total.toFixed(2);
    }
    
    // Actualizar los inputs hidden
    const productosSeleccionados = document.getElementById('productosSeleccionados');
    if (productosSeleccionados) {
        productosSeleccionados.innerHTML = inputsHidden;
    }
    
    // Habilitar/deshabilitar botón finalizar
    const btnFinalizarVenta = document.getElementById('btnFinalizarVenta');
    if (btnFinalizarVenta) {
        btnFinalizarVenta.disabled = (productos.length === 0);
    }
}

// Función para actualizar el total automáticamente
function actualizarTotal() {
    total = 0;
    productos.forEach(item => {
        item.subtotal = item.cantidad * item.precioActual;
        total += item.subtotal;
    });
    
    const totalVenta = document.getElementById('totalVenta');
    if (totalVenta) {
        totalVenta.textContent = '$' + total.toFixed(2);
    }
}

// Modificar cantidad
function modificarCantidad(index, cambio) {
    if (index >= 0 && index < productos.length) {
        const nuevaCantidad = productos[index].cantidad + cambio;
        if (nuevaCantidad >= 1 && nuevaCantidad <= productos[index].stock) {
            productos[index].cantidad = nuevaCantidad;
            productos[index].subtotal = productos[index].cantidad * productos[index].precioActual;
            actualizarCarrito();
        } else if (nuevaCantidad > productos[index].stock) {
            alert('No hay suficiente stock disponible');
        }
    }
}

// Actualizar cantidad manualmente
function actualizarCantidadManual(input, index) {
    if (index >= 0 && index < productos.length) {
        let nuevaCantidad = parseInt(input.value);
        if (nuevaCantidad >= 1 && nuevaCantidad <= productos[index].stock) {
            productos[index].cantidad = nuevaCantidad;
            productos[index].subtotal = productos[index].cantidad * productos[index].precioActual;
            actualizarCarrito();
        } else {
            input.value = productos[index].cantidad;
            alert('La cantidad debe estar entre 1 y ' + productos[index].stock);
        }
    }
}

// Actualizar precio
function actualizarPrecio(input, index) {
    if (index >= 0 && index < productos.length) {
        let nuevoPrecio = parseFloat(input.value);
        if (nuevoPrecio >= 0) {
            productos[index].precioActual = nuevoPrecio;
            productos[index].subtotal = productos[index].cantidad * nuevoPrecio;
            actualizarCarrito();
        } else {
            input.value = productos[index].precioActual.toFixed(2);
            alert('El precio no puede ser negativo');
        }
    }
}

// Eliminar producto del carrito
function eliminarProductoCarrito(index) {
   
    
    if (index >= 0 && index < productos.length) {
       
        productos.splice(index, 1);
        
        actualizarCarrito();
    } else {
        console.error("Índice fuera de rango:", index, "Longitud del array:", productos.length);
    }
}

// Función para mostrar/ocultar el segundo medio de pago
function toggleSegundoMedio() {
    const usarSegundoMedio = document.getElementById('usar_segundo_medio').checked;
    const segundoMedioContainer = document.getElementById('segundo_medio_container');
    
    if (usarSegundoMedio) {
        segundoMedioContainer.classList.remove('d-none');
        actualizarMontoPrincipal(); // Actualizar el monto principal al activar
    } else {
        segundoMedioContainer.classList.add('d-none');
        document.getElementById('monto_secundario').value = '';
        document.getElementById('monto_principal').value = total.toFixed(2);
        document.getElementById('monto_principal_display').value = total.toFixed(2);
    }
}

// Función para actualizar el monto principal cuando cambia el secundario
function actualizarMontoPrincipal() {
    if (!productos.length) return;
    
    const montoSecundario = parseFloat(document.getElementById('monto_secundario').value) || 0;
    
    // Si el monto secundario es mayor que el total, ajustarlo
    if (montoSecundario > total) {
        document.getElementById('monto_secundario').value = total.toFixed(2);
        document.getElementById('monto_principal').value = '0.00';
        document.getElementById('monto_principal_display').value = '0.00';
        return;
    }
    
    // Calcular y mostrar el monto principal
    const montoPrincipal = total - montoSecundario;
    document.getElementById('monto_principal').value = montoPrincipal.toFixed(2);
    document.getElementById('monto_principal_display').value = montoPrincipal.toFixed(2);
    
    validarMediosPago();
}

// Función para actualizar el monto secundario cuando cambia el principal
function actualizarMontoSecundario() {
    if (!productos.length) return;
    
    const montoPrincipal = parseFloat(document.getElementById('monto_principal').value) || 0;
    
    // Si el monto principal es mayor que el total, ajustarlo
    if (montoPrincipal > total) {
        document.getElementById('monto_principal').value = total.toFixed(2);
        document.getElementById('monto_principal_display').value = total.toFixed(2);
        document.getElementById('monto_secundario').value = '0.00';
        return;
    }
    
    // Calcular y mostrar el monto secundario
    const montoSecundario = total - montoPrincipal;
    document.getElementById('monto_secundario').value = montoSecundario.toFixed(2);
    
    validarMediosPago();
}

// Función para finalizar venta (actualizada con logs)
function finalizarVenta(event) {
    // Prevenir comportamiento predeterminado
    if (event) {
        event.preventDefault();
    }
    
    // Verificar productos
    if (productos.length === 0) {
        alert('Debe agregar al menos un producto a la venta');
        return;
    }
    
    // Verificar medio de pago principal
    const medioPrincipal = document.getElementById('medio_pago_principal').value;
    if (!medioPrincipal) {
        alert('Debe seleccionar un medio de pago principal');
        return;
    }
    
    // Limpiar contenedor de productos seleccionados
    const productosSeleccionados = document.getElementById('productosSeleccionados');
    if (!productosSeleccionados) {
        alert('Error: No se encontró el contenedor de productos seleccionados');
        return;
    }
    productosSeleccionados.innerHTML = '';
    
    // AGREGAR INPUTS PARA CADA PRODUCTO
    for (let i = 0; i < productos.length; i++) {
        const producto = productos[i];
        
        // Input para ID del producto
        const inputId = document.createElement('input');
        inputId.type = 'hidden';
        inputId.name = 'productos_ids';
        inputId.value = producto.id;
        productosSeleccionados.appendChild(inputId);
        
        // Input para cantidad
        const inputCantidad = document.createElement('input');
        inputCantidad.type = 'hidden';
        inputCantidad.name = 'cantidades';
        inputCantidad.value = producto.cantidad;
        productosSeleccionados.appendChild(inputCantidad);
        
        // Input para precio
        const inputPrecio = document.createElement('input');
        inputPrecio.type = 'hidden';
        inputPrecio.name = 'precios';
        inputPrecio.value = producto.precioActual;
        productosSeleccionados.appendChild(inputPrecio);
    }
    
    const usarSegundoMedio = document.getElementById('usar_segundo_medio').checked;
    let medioSecundario = '';
    let montoSecundario = 0;
    
    if (usarSegundoMedio) {
        medioSecundario = document.getElementById('medio_pago_secundario').value;
        montoSecundario = parseFloat(document.getElementById('monto_secundario').value) || 0;
        
        if (!medioSecundario || montoSecundario <= 0) {
            alert('Debe completar la información del medio de pago secundario');
            return;
        }
        
        if (montoSecundario >= total) {
            alert('El monto del medio de pago secundario no puede ser mayor o igual al total');
            return;
        }
    }
    
    // Agregar los nuevos campos al formulario
    const clienteId = document.getElementById('cliente_id').value;
    const fechaComprobante = document.getElementById('fecha_comprobante').value;
    const numeroComprobante = document.getElementById('numero_comprobante').value;
    
    // Crear inputs hidden para los nuevos campos
    const inputCliente = document.createElement('input');
    inputCliente.type = 'hidden';
    inputCliente.name = 'cliente_id';
    inputCliente.value = clienteId;
    productosSeleccionados.appendChild(inputCliente);
    
    const inputFecha = document.createElement('input');
    inputFecha.type = 'hidden';
    inputFecha.name = 'fecha_comprobante';
    inputFecha.value = fechaComprobante;
    productosSeleccionados.appendChild(inputFecha);
    
    const inputComprobante = document.createElement('input');
    inputComprobante.type = 'hidden';
    inputComprobante.name = 'numero_comprobante';
    inputComprobante.value = numeroComprobante;
    productosSeleccionados.appendChild(inputComprobante);
    
    const inputMedioPrincipal = document.createElement('input');
    inputMedioPrincipal.type = 'hidden';
    inputMedioPrincipal.name = 'medio_pago_principal';
    inputMedioPrincipal.value = medioPrincipal;
    productosSeleccionados.appendChild(inputMedioPrincipal);
    
    const inputMontoPrincipal = document.createElement('input');
    inputMontoPrincipal.type = 'hidden';
    inputMontoPrincipal.name = 'monto_principal';
    inputMontoPrincipal.value = total - montoSecundario;
    productosSeleccionados.appendChild(inputMontoPrincipal);
    
    if (usarSegundoMedio) {
        const inputMedioSecundario = document.createElement('input');
        inputMedioSecundario.type = 'hidden';
        inputMedioSecundario.name = 'medio_pago_secundario';
        inputMedioSecundario.value = medioSecundario;
        productosSeleccionados.appendChild(inputMedioSecundario);
        
        const inputMontoSecundario = document.createElement('input');
        inputMontoSecundario.type = 'hidden';
        inputMontoSecundario.name = 'monto_secundario';
        inputMontoSecundario.value = montoSecundario;
        productosSeleccionados.appendChild(inputMontoSecundario);
    }
    
    // Deshabilitar el botón y mostrar indicador de carga
    document.getElementById('btnFinalizarVenta').disabled = true;
    document.getElementById('btnFinalizarVenta').innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Procesando...';
    
    // Verificar el formulario antes de enviarlo
    const formVenta = document.getElementById('formVenta');
    if (formVenta) {
        formVenta.submit();
    } else {
        alert('Error: No se encontró el formulario de venta');
    }
}

// Función para guardar un nuevo cliente
function guardarNuevoCliente() {
    const nombre = document.getElementById('nombre_cliente').value;
    const apellido = document.getElementById('apellido_cliente').value;
    const dni = document.getElementById('dni_cliente').value;
    const telefono = document.getElementById('telefono_cliente').value;
    const email = document.getElementById('email_cliente').value;
    const direccion = document.getElementById('direccion_cliente').value;
    
    // Validar campos requeridos
    if (!nombre || !apellido) {
        alert('Nombre y apellido son campos obligatorios');
        return;
    }
    
    // Obtener el token CSRF
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    
    // Enviar datos al servidor mediante AJAX
    fetch(URL_GUARDAR_CLIENTE, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({
            nombre: nombre,
            apellido: apellido,
            dni: dni,
            telefono: telefono,
            email: email,
            direccion: direccion
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Agregar el nuevo cliente al select
            const selectCliente = document.getElementById('cliente_id');
            const option = document.createElement('option');
            option.value = data.cliente_id;
            option.text = nombre + ' ' + apellido;
            selectCliente.appendChild(option);
            selectCliente.value = data.cliente_id;

            // Cerrar el modal
            $('#ClienteModal').modal('hide');

            // Limpiar el formulario
            document.getElementById('formNuevoCliente').reset();
        } else {
            alert('Error al guardar el cliente: ' + data.error);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error al procesar la solicitud');
    });
}

// Función para alternar entre precio de lista y precio de contado
function alternarPrecio(index) {
    if (index >= 0 && index < productos.length) {
        // Cambiar el flag
        productos[index].usandoPrecioContado = !productos[index].usandoPrecioContado;
        
        // Establecer el precio según el flag
        if (productos[index].usandoPrecioContado) {
            productos[index].precioActual = productos[index].precioContado;
        } else {
            productos[index].precioActual = productos[index].precioLista;
        }
        
        // Actualizar el subtotal
        productos[index].subtotal = productos[index].cantidad * productos[index].precioActual;
        
        // Actualizar la vista
        actualizarCarrito();
    }
}

// Función para cambiar todos los productos a precio contado
function cambiarTodosAPrecioContado() {
    if (productos.length === 0) return;
    
    for (let i = 0; i < productos.length; i++) {
        productos[i].usandoPrecioContado = true;
        productos[i].precioActual = productos[i].precioContado;
        productos[i].subtotal = productos[i].cantidad * productos[i].precioActual;
    }
    
    actualizarCarrito();
}

// Función para cambiar todos los productos a precio lista
function cambiarTodosAPrecioLista() {
    if (productos.length === 0) return;
    
    for (let i = 0; i < productos.length; i++) {
        productos[i].usandoPrecioContado = false;
        productos[i].precioActual = productos[i].precioLista;
        productos[i].subtotal = productos[i].cantidad * productos[i].precioActual;
    }
    
    actualizarCarrito();
}

// Función para validar medios de pago
function validarMediosPago() {
    // Implementar validación si es necesario
    // Por ahora, no hacemos nada
}

// Agregar event listeners cuando el DOM esté cargado
document.addEventListener('DOMContentLoaded', function() {
    // Event listener para el botón finalizar venta
    const btnFinalizar = document.getElementById('btnFinalizarVenta');
    if (btnFinalizar) {
        btnFinalizar.addEventListener('click', finalizarVenta);
    }
    
    // Aquí puedes agregar otros event listeners que necesites
});
