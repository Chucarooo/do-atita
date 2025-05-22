from django.shortcuts import render, redirect,get_object_or_404
from .models import *
from .forms import *
from django.contrib import messages

from django.views.generic import ListView
from django.http import JsonResponse, HttpResponse
from weasyprint.text.fonts import FontConfiguration
from django.template.loader import get_template
from weasyprint import HTML, CSS
from django.conf import settings
import os
from django.db.models import Sum, Count, F, Avg, DecimalField
from django.db.models.functions import Coalesce
from django.utils import timezone
from datetime import datetime, time, timedelta
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db import transaction
from django.views.decorators.csrf import csrf_exempt
import json
from django.urls import reverse
from decimal import Decimal

# Create your views here.

def obtener_ventas_del_dia():
    """
    Calcula el total de ventas del día actual.
    Retorna la suma de los montos de todas las ventas realizadas hoy.
    """
    hoy = timezone.now().date()
    inicio_dia = datetime.combine(hoy, time.min)
    fin_dia = datetime.combine(hoy, time.max)

    total_ventas = Venta.objects.filter(
        Fecha__range=(inicio_dia, fin_dia)
    ).aggregate(
        total=Sum('ImporteTotal')
    )['total'] or 0

    return total_ventas

def contar_productos_bajos_stock():
    """
    Cuenta cuántos productos están por debajo de su cantidad mínima sugerida.
    Retorna el número de productos que necesitan reposición.
    """
    # Usar el método de filtrado directo en la base de datos
    productos_bajos = Producto.objects.filter(
        Cantidad__lte=models.F('CantidadMinimaSugerida')
    ).count()

    return productos_bajos

def obtener_productos_stock_bajo():
    """
    Obtiene la lista de productos con stock bajo para mostrar en el dashboard.
    Retorna los 5 productos más críticos en términos de stock.
    """
    # Usar el método de filtrado directo en la base de datos
    productos = Producto.objects.filter(
        Cantidad__lte=models.F('CantidadMinimaSugerida')
    ).order_by('Cantidad')[:5]  # Ordenamos por cantidad ascendente

    return productos

@login_required
def index_view(request):
    context = {
        'ventas_dia': obtener_ventas_del_dia(),
        'productos_bajos': contar_productos_bajos_stock(),
        'total_productos': Producto.objects.count(),
        'total_clientes': Cliente.objects.count(),
        'ultimas_ventas': Venta.objects.all().order_by('-Fecha')[:5],
        'productos_stock_bajo': obtener_productos_stock_bajo(),
    }
    return render(request, 'index.html', context)

def clientes_view(request):
    clientes = Cliente.objects.all()
    form_personal = AddClienteForm()
    form_editar = EditClienteForm()
    context = {
        'clientes': clientes,
        'form_personal': form_personal,
        'form_editar': form_editar,
    }
    return render(request, 'clientes.html', context)

def add_cliente_view(request):
    if request.method == "POST":
        form = AddClienteForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Cliente agregado exitosamente.")
            except Exception as e:
                messages.error(request, f"Error al agregar el cliente: {str(e)}")
        else:
            messages.error(request, "Error en el formulario. Verifique los datos ingresados.")
    return redirect('Clientes')

def edit_cliente_view(request):
    id_personal_editar = request.POST.get('id_personal_editar')
    if id_personal_editar:
        if request.method == "POST":
            cliente = Cliente.objects.get(pk=request.POST.get('id_personal_editar'))
            form = EditClienteForm(request.POST, request.FILES, instance=cliente)
            if form.is_valid():
                try:
                    form.save()
                except Exception as e:
                    messages.success(request, f"Error al modificar el cliente: {str(e)}")
            else:
                messages.error(request, "Error en el formulario. Verifique los datos ingresados.")
    else:
        messages.error(request, "Error en el formulario. Verifique los datos ingresados.")
    return redirect('Clientes')

def delete_cliente_view(request):
    cliente = Cliente.objects.get(pk=request.POST.get('id_personal_eliminar'))
    cliente.delete()
    messages.success(request, "Cliente eliminado exitosamente.")
    return redirect('Clientes')

def proveedores_view(request):
    proveedores = Proveedor.objects.all()
    form_personal = AddProveedorForm()
    form_editar = EditProveedorForm()
    context = {
        'proveedores': proveedores,
        'form_personal': form_personal,
        'form_editar': form_editar,
    }
    return render(request, 'proveedores.html', context)

def add_proveedor_view(request):
    if request.method == "POST":
        form = AddProveedorForm(request.POST)
        if form.is_valid():
            try:
                proveedor = form.save()
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    # Si es una solicitud AJAX, devolver JSON
                    proveedores = Proveedor.objects.all()
                    return JsonResponse({
                        'success': True,
                        'message': 'Proveedor agregado exitosamente.',
                        'nuevo_proveedor_id': proveedor.id,
                        'proveedores': [{'id': p.id, 'RazonSocial': p.RazonSocial} for p in proveedores]
                    })
                else:
                    messages.success(request, "Proveedor agregado exitosamente.")
            except Exception as e:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'message': f'Error al guardar el proveedor: {str(e)}'
                    })
                messages.error(request, f"Error al guardar el proveedor: {str(e)}")
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': 'Error en el formulario. Verifique los datos ingresados.'
                })
            messages.error(request, "Error en el formulario. Verifique los datos ingresados.")
    return redirect('Proveedores')

def edit_proveedor_view(request):
    id_proveedor_editar = request.POST.get('id_proveedor_editar')
    if id_proveedor_editar:
        if request.method == "POST":
            proveedor = Proveedor.objects.get(pk=id_proveedor_editar)
            form = EditProveedorForm(request.POST, instance=proveedor)
            if form.is_valid():
                try:
                    form.save()
                    messages.success(request, "Proveedor modificado exitosamente.")
                except Exception as e:
                    messages.error(request, f"Error al modificar el proveedor: {str(e)}")
            else:
                messages.error(request, "Error en el formulario. Verifique los datos ingresados.")
    else:
        messages.error(request, "Error en el formulario. Verifique los datos ingresados.")
    return redirect('Proveedores')

def delete_proveedor_view(request):
    proveedor = Proveedor.objects.get(pk=request.POST.get('id_proveedor_eliminar'))
    proveedor.delete()
    messages.success(request, "Proveedor eliminado exitosamente.")
    return redirect('Proveedores')

@login_required
def productos_view(request):
    # Si hay parámetros de venta exitosa, redirigir a la misma URL sin parámetros
    if 'venta_exitosa' in request.GET:
        return redirect('productos')
        
    # Limpiar mensajes de venta exitosa si existen
    if 'venta_exitosa' in request.session:
        del request.session['venta_exitosa']
        
    productos = Producto.objects.all()
    form_producto = AddProductoForm()
    form_editar = EditProductoForm()
    context = {
        'productos': productos,
        'form_producto': form_producto,
        'form_editar': form_editar,
    }
    return render(request, 'productos.html', context)

def add_producto_view(request):
    if request.method == "POST":
        form = AddProductoForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Producto agregado exitosamente.")
            except Exception as e:
                messages.error(request, f"Error al guardar el producto: {str(e)}")
        else:
            messages.error(request, "Error en el formulario. Verifique los datos ingresados.")
    return redirect('Productos')

@login_required
def EditProducto(request):
    if request.method == 'POST':
        try:
            producto_id = request.POST.get('id_producto_editar')
            if not producto_id:
                return JsonResponse({'success': False, 'error': 'No se proporcionó ID de producto'})
            
            producto = Producto.objects.get(id=producto_id)
            
            # Actualizar los campos del producto
            producto.Nombre = request.POST.get('Nombre')
            producto.Marca_id = request.POST.get('Marca')
            producto.Categoria_id = request.POST.get('Categoria')
            producto.CodigoDeBarras = request.POST.get('CodigoDeBarras')
            producto.PrecioCosto = request.POST.get('PrecioCosto')
            producto.PrecioDeLista = request.POST.get('PrecioDeLista')
            producto.PrecioDeContado = request.POST.get('PrecioDeContado')
            producto.Cantidad = request.POST.get('Cantidad')
            producto.CantidadMinimaSugerida = request.POST.get('CantidadMinimaSugerida')
            producto.UnidadDeMedida_id = request.POST.get('UnidadDeMedida')
            producto.FechaUltimaModificacion = request.POST.get('FechaUltimaModificacion')
            
            producto.save()
            
            messages.success(request, 'Producto actualizado correctamente')
            return JsonResponse({'success': True})
            
        except Producto.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Producto no encontrado'})
        except Exception as e:
            if form.is_valid():
                form.save()
                messages.success(request, 'Producto actualizado correctamente')
                return redirect('productos')
            else:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f'{field}: {error}')
                return redirect('productos')
                
        except Producto.DoesNotExist:
            messages.error(request, 'Producto no encontrado')
            return redirect('productos')
        except Exception as e:
            messages.error(request, f'Error al actualizar el producto: {str(e)}')
            return redirect('productos')
    return redirect('productos')

def delete_producto_view(request):
    try:
        producto = Producto.objects.get(pk=request.POST.get('id_producto_eliminar'))
        producto.delete()
        return JsonResponse({'success': True, 'message': 'Producto eliminado exitosamente.'})
    except Producto.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'El producto no existe.'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
def categorias_view(request):
    categorias = Categoria.objects.all()
    form_personal = AddCategoriaForm()
    form_editar = EditCategoriaForm()
    context = {
        'categorias': categorias,
        'form_personal': form_personal,
        'form_editar': form_editar,
    }
    return render(request, 'categorias.html', context)

@csrf_exempt
def add_categoria_view(request):
    if request.method == "POST":
        try:
            nombre = request.POST.get('Nombre')
            categoria = Categoria.objects.create(Nombre=nombre)
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'id': categoria.id,
                    'nombre': categoria.Nombre,
                    'seleccionar': True
                })
            messages.success(request, "Categoria agregada exitosamente.")
        except Exception as e:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': str(e)})
            messages.error(request, f"Error al guardar la categoria: {str(e)}")
    return redirect('Productos')

def edit_categoria_view(request):
    id_categoria_editar = request.POST.get('id_categoria_editar')
    if id_categoria_editar:
        if request.method == "POST":
            categoria = Categoria.objects.get(pk=request.POST.get('id_categoria_editar'))
            form = EditCategoriaForm(request.POST, request.FILES, instance=categoria)
            if form.is_valid():
                try:
                    form.save()
                except Exception as e:
                    messages.success(request, f"Error al modificar la categoría: {str(e)}")
            else:
                messages.error(request, "Error en el formulario. Verifique los datos ingresados.")
    else:
        messages.error(request, "Error en el formulario. Verifique los datos id_categoria_editar.")
    return redirect('Categorias')

def delete_categoria_view(request):
    categoria = request.POST.get('id_categoria_eliminar')
    if categoria:
        categoria = Categoria.objects.get(pk=request.POST.get('id_categoria_eliminar'))
        categoria.delete()
        messages.success(request, "Categoría eliminada exitosamente.")
    else:
        messages.error(request, "Error al eliminar la categoría.")
    return redirect('Categorias')

#Ventas
@login_required
def ventas_view(request):
    if request.GET.get('venta_exitosa'):
        return redirect('ventas')
    
    caja_abierta = Caja.objects.filter(Cajero=request.user, Estado='ABIERTA').first()
    productos = Producto.objects.all()
    clientes = Cliente.objects.all()
    medios_pago = MedioDePago.objects.filter(Activo=True)
    
    # Obtener la fecha actual
    hoy = timezone.now().date()
    fecha_str = hoy.strftime('%Y%m%d')
    
    # Obtener el último comprobante del día actual
    inicio_dia = datetime.combine(hoy, time.min)
    fin_dia = datetime.combine(hoy, time.max)
    
    ultimo_comprobante = Venta.objects.filter(
        Fecha__range=(inicio_dia, fin_dia)
    ).order_by('-NumeroComprobate').first()
    
    if ultimo_comprobante:
        # Extraer el número secuencial del último comprobante
        partes = ultimo_comprobante.NumeroComprobate.split('-')
        if len(partes) == 3:  # Formato A-YYYYMMDD-XXXXX
            ultimo_numero = int(partes[2])
        else:  # Formato antiguo A-XXXXX
            ultimo_numero = int(partes[1])
        siguiente_numero = f"A-{fecha_str}-{str(ultimo_numero + 1).zfill(5)}"
    else:
        siguiente_numero = f"A-{fecha_str}-{str(1).zfill(5)}"
    
    if request.method == 'POST':
        try:
            cliente_id = request.POST.get('cliente_id')
            fecha_comprobante = request.POST.get('fecha_comprobante')
            medio_pago_principal = request.POST.get('medio_pago_principal')
            monto_principal = request.POST.get('monto_principal')
            medio_pago_secundario = request.POST.get('medio_pago_secundario')
            monto_secundario = request.POST.get('monto_secundario')
            productos_data = json.loads(request.POST.get('productos', '[]'))
            
            if not productos_data:
                return JsonResponse({'success': False, 'error': 'No hay productos en la venta'})
            
            if not medio_pago_principal or not monto_principal:
                return JsonResponse({'success': False, 'error': 'Debe especificar un medio de pago principal'})
            
            # Validar datos de productos
            for producto_data in productos_data:
                if not all(key in producto_data for key in ['id', 'cantidad', 'precio']):
                    return JsonResponse({
                        'success': False, 
                        'error': 'Faltan datos requeridos en los productos'
                    })
                
                try:
                    float(producto_data['precio'])
                    int(producto_data['cantidad'])
                except (ValueError, TypeError):
                    return JsonResponse({
                        'success': False, 
                        'error': 'Datos inválidos en los productos'
                    })
            
            total_venta = sum(float(p['precio']) * int(p['cantidad']) for p in productos_data)
            
            # Crear la venta con el número de comprobante generado
            venta = Venta.objects.create(
                NumeroComprobate=siguiente_numero,
                Cliente_id=cliente_id if cliente_id else None,
                ImporteTotal=total_venta,
                Caja=caja_abierta,
                Cajero=request.user
            )
            
            # Procesar cada producto y actualizar el stock
            for producto_data in productos_data:
                producto = Producto.objects.get(id=producto_data['id'])
                cantidad = int(producto_data['cantidad'])
                precio = float(producto_data['precio'])
                
                # Verificar stock disponible
                if producto.Cantidad < cantidad:
                    venta.delete()  # Eliminar la venta si no hay stock suficiente
                    return JsonResponse({
                        'success': False,
                        'error': f'Stock insuficiente para {producto.Nombre}. Stock disponible: {producto.Cantidad}'
                    })
                
                # Crear el detalle de venta
                DetalleVenta.objects.create(
                    Venta=venta,
                    Producto=producto,
                    Cantidad=cantidad,
                    PrecioUnitario=precio,
                    Subtotal=precio * cantidad
                )
                
                # Actualizar el stock del producto
                stock_anterior = producto.Cantidad
                producto.Cantidad -= cantidad
                producto.save()
                
                # Registrar el movimiento de stock
                MovimientoStock.objects.create(
                    Fecha=venta.Fecha,
                    Producto=producto,
                    Tipo='SALIDA',
                    Cantidad=cantidad,
                    StockAnterior=stock_anterior,
                    StockResultante=producto.Cantidad,
                    OrigenMovimiento='VENTA',
                    Usuario=request.user,
                    Observaciones=f'Venta #{venta.id}'
                )
            
            # Crear los pagos
            PagoVenta.objects.create(
                Venta=venta,
                MedioDePago_id=medio_pago_principal,
                Monto=monto_principal
            )
            
            if medio_pago_secundario and monto_secundario:
                PagoVenta.objects.create(
                    Venta=venta,
                    MedioDePago_id=medio_pago_secundario,
                    Monto=monto_secundario
                )
            
            return JsonResponse({
                'success': True,
                'venta_id': venta.id
            })
                
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    context = {
        'productos': productos,
        'clientes': clientes,
        'medios_pago': medios_pago,
        'ultimo_comprobante': siguiente_numero,
        'caja': caja_abierta
    }
    
    return render(request, 'ventas.html', context)

def login_view(request):
    # Redirigir a Index si el usuario ya está autenticado
    if request.user.is_authenticated:
        return redirect('Index')
        
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                auth_login(request, user)
                # Redirigir a la página solicitada originalmente o a Index
                next_page = request.GET.get('next', 'Index')
                return redirect(next_page)
            else:
                messages.error(request, 'Usuario o contraseña incorrectos')
    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form})

def logout_view(request):
    auth_logout(request)
    return redirect('Login')

def register_view(request):
    # Redirigir a Index si el usuario ya está autenticado
    if request.user.is_authenticated:
        return redirect('Index')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Cuenta creada para {username}. Ahora puedes iniciar sesión.')
            return redirect('Login')
    else:
        form = RegisterForm()

    return render(request, 'register.html', {'form': form})

def get_medio_pago_info(request):
    medio_pago_id = request.GET.get('id')
    medio_pago = MedioDePago.objects.get(id=medio_pago_id)

    # Determinar el tipo basado en el nombre (o agregar un campo tipo al modelo)
    tipo = 'OTRO'
    if 'efectivo' in medio_pago.Nombre.lower():
        tipo = 'EFECTIVO'
    elif 'qr' in medio_pago.Nombre.lower():
        tipo = 'QR'
    elif 'transferencia' in medio_pago.Nombre.lower():
        tipo = 'TRANSFERENCIA'

    return JsonResponse({
        'id': medio_pago.id,
        'nombre': medio_pago.Nombre,
        'tipo': tipo
    })

@login_required
def caja_view(request):
    # Verificar si hay una caja abierta para este usuario
    caja_abierta = Caja.objects.filter(Cajero=request.user, Estado='ABIERTA').first()
    
    if request.method == 'POST':
        accion = request.POST.get('accion')
        
        if accion == 'abrir':
            # Verificar que no haya otra caja abierta
            if caja_abierta:
                messages.warning(request, "Ya tienes una caja abierta.")
                return redirect('caja')
            
            # Abrir nueva caja
            saldo_inicial = request.POST.get('saldo_inicial')
            try:
                saldo_inicial = decimal.Decimal(saldo_inicial)
                if saldo_inicial < 0:
                    raise ValueError("El saldo inicial no puede ser negativo")
                
                caja = Caja.objects.create(
                    Cajero=request.user,
                    SaldoInicial=saldo_inicial,
                    Estado='ABIERTA'
                )
                messages.success(request, f"Caja #{caja.id} abierta correctamente.")
                return redirect('caja')
            except Exception as e:
                messages.error(request, f"Error al abrir caja: {str(e)}")
        
        elif accion == 'cerrar':
            # Verificar que haya una caja abierta
            if not caja_abierta:
                messages.warning(request, "No tienes una caja abierta para cerrar.")
                return redirect('caja')
            
            # Cerrar caja
            saldo_final_real = request.POST.get('saldo_final_real')
            observaciones = request.POST.get('observaciones', '')
            
            try:
                saldo_final_real = decimal.Decimal(saldo_final_real)
                if saldo_final_real < 0:
                    raise ValueError("El saldo final no puede ser negativo")
                
                caja_abierta.CerrarCaja(saldo_final_real, observaciones)
                messages.success(request, f"Caja #{caja_abierta.id} cerrada correctamente.")
                return redirect('caja')
            except Exception as e:
                messages.error(request, f"Error al cerrar caja: {str(e)}")
    
    # Obtener datos para la vista
    if caja_abierta:
        # Calcular totales
        total_efectivo = caja_abierta.GetTotalEfectivo()
        
        # Debug - imprimir valores
        print(f"DEBUG - Saldo Inicial: {caja_abierta.SaldoInicial}")
        print(f"DEBUG - Total Efectivo: {total_efectivo}")
        
        # Calcular total de egresos en efectivo
        total_egresos = MovimientoCaja.objects.filter(
            Caja=caja_abierta,
            TipoMovimiento='EGRESO',
            MedioDePago__Tipo='EFECTIVO'
        ).aggregate(total=Sum('Monto'))['total'] or 0
        
        print(f"DEBUG - Total Egresos: {total_egresos}")
        
        # Calcular saldo esperado en efectivo (saldo inicial + ingresos - egresos)
        saldo_esperado = float(caja_abierta.SaldoInicial) + float(total_efectivo) - float(total_egresos)
        
        print(f"DEBUG - Saldo Esperado: {saldo_esperado}")
        
        
        total_transferencia = caja_abierta.GetTotalTransferencia()
        
        
        # Obtener las ventas asociadas a esta caja
        ventas = Venta.objects.filter(Caja=caja_abierta).order_by('-Fecha')
        
        # Obtener los movimientos de caja
        movimientos = MovimientoCaja.objects.filter(Caja=caja_abierta).order_by('-Fecha')
        
        # Agregar total de ventas al contexto
        total_ventas = caja_abierta.GetTotalVentas()
        
        context = {
            'caja': caja_abierta,
            'total_efectivo': total_efectivo,
            
            'total_transferencia': total_transferencia,
            
            'saldo_esperado': saldo_esperado,
            'resumen_por_medio': caja_abierta.GetResumenPorMedioPago(),
            'ventas': ventas,
            'movimientos': movimientos,
            'total_ventas': total_ventas
        }
    else:
        context = {}
    
    return render(request, 'caja.html', context)

@staff_member_required
def historial_cajas_view(request):
    # Filtros
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    cajero_id = request.GET.get('cajero_id')
    estado = request.GET.get('estado')
    
    # Consulta base
    cajas = Caja.objects.all()
    
    # Aplicar filtros
    if fecha_inicio:
        cajas = cajas.filter(FechaApertura__date__gte=fecha_inicio)
    
    if fecha_fin:
        cajas = cajas.filter(FechaApertura__date__lte=fecha_fin)
    
    if cajero_id:
        cajas = cajas.filter(Cajero_id=cajero_id)
    
    if estado:
        cajas = cajas.filter(Estado=estado)
    
    # Ordenar por fecha de apertura descendente
    cajas = cajas.order_by('-FechaApertura')
    
    # Obtener lista de cajeros para el filtro
    cajeros = User.objects.filter(is_staff=True)
    
    context = {
        'cajas': cajas,
        'cajeros': cajeros,
        'filtros': {
            'fecha_inicio': fecha_inicio,
            'fecha_fin': fecha_fin,
            'cajero_id': cajero_id,
            'estado': estado
        }
    }

    return render(request, 'historial_cajas.html', context)

@staff_member_required
def detalle_caja_view(request, caja_id):
    """Vista para mostrar el detalle de una caja específica (para AJAX)"""
    try:
        caja = Caja.objects.get(id=caja_id)
        
        # Obtener ventas asociadas a esta caja
        ventas = Venta.objects.filter(Caja=caja).order_by('-Fecha')
        
        # Obtener movimientos de caja
        movimientos = MovimientoCaja.objects.filter(Caja=caja).order_by('-Fecha')
        
        # Calcular totales
        total_efectivo = caja.GetTotalEfectivo()
        
        total_transferencia = caja.GetTotalTransferencia()
       
        
        # Calcular saldo esperado en efectivo (saldo inicial + ventas en efectivo)
        saldo_esperado = caja.SaldoInicial + total_efectivo
        
        context = {
            'caja': caja,
            'ventas': ventas,
            'movimientos': movimientos,
            'total_efectivo': total_efectivo,
            
            'total_transferencia': total_transferencia,
            
            'saldo_esperado': saldo_esperado,
            'resumen_por_medio': caja.GetResumenPorMedioPago(),
        }
        
        return render(request, 'detalle_caja_ajax.html', context)
    except Caja.DoesNotExist:
        return HttpResponse('<div class="alert alert-danger">La caja solicitada no existe</div>')

# Agregar esta vista para guardar clientes mediante AJAX
@csrf_exempt
def guardar_cliente_ajax(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            cliente = Cliente(
                Nombre=data['nombre'],
                Apellido=data['apellido'],
                DNI=data.get('dni', ''),
                Telefono=data.get('telefono', ''),
                Email=data.get('email', ''),
                Direccion=data.get('direccion', '')
            )
            cliente.save()
            return JsonResponse({
                'success': True,
                'cliente_id': cliente.id
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    return JsonResponse({'success': False, 'error': 'Método no permitido'})

# Vistas para Historial de Movimientos de Stock
@login_required
def historial_movimientos(request):
    # Obtener parámetros de filtro
    producto_id = request.GET.get('producto')
    tipo = request.GET.get('tipo')
    origen = request.GET.get('origen')
    fecha_desde = request.GET.get('fecha_desde')
    fecha_hasta = request.GET.get('fecha_hasta')
    
    # Iniciar con todos los movimientos
    movimientos = MovimientoStock.objects.all()
    
    # Aplicar filtros
    if producto_id:
        movimientos = movimientos.filter(Producto_id=producto_id)
    if tipo:
        movimientos = movimientos.filter(Tipo=tipo)
    if origen:
        movimientos = movimientos.filter(OrigenMovimiento=origen)
    if fecha_desde:
        movimientos = movimientos.filter(Fecha__gte=fecha_desde)
    if fecha_hasta:
        movimientos = movimientos.filter(Fecha__lte=fecha_hasta)
    
    # Ordenar por fecha descendente
    movimientos = movimientos.order_by('-Fecha')
    
    # Paginación
    paginator = Paginator(movimientos, 20)  # 20 movimientos por página
    page = request.GET.get('page')
    try:
        movimientos = paginator.page(page)
    except PageNotAnInteger:
        movimientos = paginator.page(1)
    except EmptyPage:
        movimientos = paginator.page(paginator.num_pages)
    
    # Formulario de búsqueda
    form = BusquedaMovimientosForm(request.GET)
    
    context = {
        'movimientos': movimientos,
        'form': form,
        'titulo': 'Historial de Movimientos de Stock'
    }
    
    return render(request, 'ventas/historial_movimientos.html', context)

# Vistas para Ajustes de Inventario
@login_required
def lista_ajustes(request):
    ajustes = AjusteInventario.objects.all().order_by('-Fecha')
    
    # Paginación
    paginator = Paginator(ajustes, 20)
    page = request.GET.get('page')
    ajustes_paginados = paginator.get_page(page)
    
    context = {
        'ajustes': ajustes_paginados,
    }
    
    return render(request, 'ventas/lista_ajustes.html', context)

@login_required
def crear_ajuste(request):
    if request.method == 'POST':
        form = AjusteInventarioForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                # Crear el ajuste pero no guardarlo aún
                ajuste = form.save(commit=False)
                ajuste.Usuario = request.user
                
                # Guardar el ajuste
                ajuste.save()
                
                messages.success(request, "Ajuste de inventario creado. Ahora agregue los detalles.")
                return redirect('detalle_ajuste', ajuste_id=ajuste.id)
        else:
            messages.error(request, "Error en el formulario. Verifique los datos ingresados.")
    else:
        form = AjusteInventarioForm()
    
    context = {
        'form': form,
    }
    
    return render(request, 'ventas/crear_ajuste.html', context)

@login_required
def detalle_ajuste(request, ajuste_id):
    ajuste = get_object_or_404(AjusteInventario, pk=ajuste_id)
    detalles = DetalleAjuste.objects.filter(Ajuste=ajuste)
    
    if request.method == 'POST':
        form = DetalleAjusteForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    detalle = form.save(commit=False)
                    detalle.Ajuste = ajuste
                    detalle.CantidadAnterior = detalle.Producto.Cantidad
                    detalle.save()
                    
                    messages.success(request, "Detalle agregado correctamente.")
                    return redirect('detalle_ajuste', ajuste_id=ajuste.id)
            except ValidationError as e:
                messages.error(request, str(e))
        else:
            messages.error(request, "Error en el formulario. Verifique los datos ingresados.")
    else:
        form = DetalleAjusteForm()
    
    context = {
        'ajuste': ajuste,
        'detalles': detalles,
        'form': form,
    }
    
    return render(request, 'ventas/detalle_ajuste.html', context)

# Vistas para Inventario Físico
@login_required
def lista_inventarios(request):
    inventarios = InventarioFisico.objects.all().order_by('-Fecha')
    
    # Paginación
    paginator = Paginator(inventarios, 20)
    page = request.GET.get('page')
    inventarios_paginados = paginator.get_page(page)
    
    context = {
        'inventarios': inventarios_paginados,
    }
    
    return render(request, 'ventas/lista_inventarios.html', context)

@login_required
def crear_inventario(request):
    if request.method == 'POST':
        form = InventarioFisicoForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                # Crear el inventario pero no guardarlo aún
                inventario = form.save(commit=False)
                inventario.Usuario = request.user
                inventario.Estado = 'BORRADOR'
                
                # Guardar el inventario
                inventario.save()
                
                messages.success(request, "Inventario físico creado. Ahora agregue los productos.")
                return redirect('detalle_inventario', inventario_id=inventario.id)
        else:
            messages.error(request, "Error en el formulario. Verifique los datos ingresados.")
    else:
        form = InventarioFisicoForm()
    
    context = {
        'form': form,
    }
    
    return render(request, 'ventas/crear_inventario.html', context)

@login_required
def detalle_inventario(request, inventario_id):
    inventario = get_object_or_404(InventarioFisico, pk=inventario_id)
    
    # Si el inventario no está en estado borrador, no permitir modificaciones
    if inventario.Estado != 'BORRADOR':
        messages.warning(request, "Este inventario ya está finalizado y no puede ser modificado.")
        return redirect('lista_inventarios')
    
    detalles = DetalleInventarioFisico.objects.filter(Inventario=inventario)
    
    if request.method == 'POST':
        # Verificar si es una solicitud para agregar un producto
        if 'agregar_producto' in request.POST:
            producto_id = request.POST.get('producto')
            
            # Verificar si el producto ya está en el inventario
            if DetalleInventarioFisico.objects.filter(Inventario=inventario, Producto_id=producto_id).exists():
                messages.error(request, "Este producto ya está en el inventario.")
            else:
                try:
                    producto = Producto.objects.get(pk=producto_id)
                    
                    # Crear el detalle con la cantidad del sistema
                    DetalleInventarioFisico.objects.create(
                        Inventario=inventario,
                        Producto=producto,
                        CantidadSistema=producto.Cantidad,
                        CantidadFisica=0  # Inicialmente 0, el usuario debe ingresar la cantidad real
                    )
                    
                    messages.success(request, f"Producto {producto.Nombre} agregado al inventario.")
                except Producto.DoesNotExist:
                    messages.error(request, "Producto no encontrado.")
        
        # Verificar si es una solicitud para actualizar la cantidad física
        elif 'actualizar_cantidad' in request.POST:
            detalle_id = request.POST.get('detalle_id')
            cantidad_fisica = request.POST.get('cantidad_fisica')
            
            try:
                detalle = DetalleInventarioFisico.objects.get(pk=detalle_id, Inventario=inventario)
                detalle.CantidadFisica = cantidad_fisica
                detalle.save()
                
                messages.success(request, f"Cantidad actualizada para {detalle.Producto.Nombre}.")
            except DetalleInventarioFisico.DoesNotExist:
                messages.error(request, "Detalle no encontrado.")
        
        # Verificar si es una solicitud para finalizar el inventario
        elif 'finalizar_inventario' in request.POST:
            try:
                inventario.finalizar(request.user)
                messages.success(request, "Inventario finalizado y ajustes aplicados correctamente.")
                return redirect('lista_inventarios')
            except ValidationError as e:
                messages.error(request, str(e))
    
    # Obtener productos que no están en el inventario para el selector
    productos_en_inventario = detalles.values_list('Producto_id', flat=True)
    productos_disponibles = Producto.objects.exclude(id__in=productos_en_inventario).order_by('Nombre')
    
    context = {
        'inventario': inventario,
        'detalles': detalles,
        'productos_disponibles': productos_disponibles,
    }
    
    return render(request, 'ventas/detalle_inventario.html', context)

# Vistas para Transferencias entre Productos
@login_required
def lista_transferencias(request):
    transferencias = TransferenciaProducto.objects.all().order_by('-Fecha')
    
    # Paginación
    paginator = Paginator(transferencias, 20)
    page = request.GET.get('page')
    transferencias_paginadas = paginator.get_page(page)
    
    context = {
        'transferencias': transferencias_paginadas,
    }
    
    return render(request, 'ventas/lista_transferencias.html', context)

@login_required
def crear_transferencia(request):
    if request.method == 'POST':
        form = TransferenciaProductoForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    transferencia = form.save(commit=False)
                    transferencia.Usuario = request.user
                    transferencia.Estado = 'PENDIENTE'
                    transferencia.save()
                    
                    messages.success(request, "Transferencia creada correctamente.")
                    return redirect('lista_transferencias')
            except ValidationError as e:
                messages.error(request, str(e))
        else:
            messages.error(request, "Error en el formulario. Verifique los datos ingresados.")
    else:
        form = TransferenciaProductoForm()
    
    context = {
        'form': form,
    }
    
    return render(request, 'ventas/crear_transferencia.html', context)

@login_required
def completar_transferencia(request, transferencia_id):
    transferencia = get_object_or_404(TransferenciaProducto, pk=transferencia_id)
    
    try:
        transferencia.completar()
        messages.success(request, "Transferencia completada correctamente.")
    except ValidationError as e:
        messages.error(request, str(e))
    
    return redirect('lista_transferencias')

@login_required
def cancelar_transferencia(request, transferencia_id):
    transferencia = get_object_or_404(TransferenciaProducto, pk=transferencia_id)
    
    try:
        transferencia.cancelar()
        messages.success(request, "Transferencia cancelada correctamente.")
    except ValidationError as e:
        messages.error(request, str(e))
    
    return redirect('lista_transferencias')

# Vistas para Reservas de Stock
@login_required
def lista_reservas(request):
    reservas = ReservaStock.objects.all().order_by('-Fecha')
    
    # Paginación
    paginator = Paginator(reservas, 20)
    page = request.GET.get('page')
    reservas_paginadas = paginator.get_page(page)
    
    context = {
        'reservas': reservas_paginadas,
    }
    
    return render(request, 'ventas/lista_reservas.html', context)

@login_required
def crear_reserva(request):
    if request.method == 'POST':
        form = ReservaStockForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    # Verificar stock disponible
                    producto = form.cleaned_data['Producto']
                    cantidad = form.cleaned_data['Cantidad']
                    
                    if not producto.stock_disponible(cantidad):
                        raise ValidationError(f"Stock insuficiente para {producto.Nombre}")
                    
                    # Crear la reserva
                    reserva = form.save(commit=False)
                    reserva.Usuario = request.user
                    reserva.Estado = 'ACTIVA'
                    reserva.save()
                    
                    messages.success(request, "Reserva creada correctamente.")
                    return redirect('lista_reservas')
            except ValidationError as e:
                messages.error(request, str(e))
        else:
            messages.error(request, "Error en el formulario. Verifique los datos ingresados.")
    else:
        form = ReservaStockForm()
    
    context = {
        'form': form,
    }
    
    return render(request, 'ventas/crear_reserva.html', context)

@login_required
def cancelar_reserva(request, reserva_id):
    reserva = get_object_or_404(ReservaStock, pk=reserva_id)
    
    try:
        reserva.cancelar()
        messages.success(request, "Reserva cancelada correctamente.")
    except ValidationError as e:
        messages.error(request, str(e))
    
    return redirect('lista_reservas')

@login_required
def utilizar_reserva(request, reserva_id):
    reserva = get_object_or_404(ReservaStock, pk=reserva_id)
    
    try:
        reserva.utilizar()
        messages.success(request, "Reserva marcada como utilizada correctamente.")
    except ValidationError as e:
        messages.error(request, str(e))
    
    return redirect('lista_reservas')

# Función para obtener subcategorías según la categoría seleccionada
def get_subcategorias(request):
    categoria_id = request.GET.get('categoria_id')
    subcategorias = []
    categorias = list(Categoria.objects.all().values('id', 'Nombre'))
    
    if categoria_id:
        try:
            subcategorias = list(SubCategoria.objects.filter(Categoria_id=categoria_id).values('id', 'Nombre'))
        except Exception as e:
            print(f"Error al obtener subcategorías: {str(e)}")
    
    return JsonResponse({
        'subcategorias': subcategorias,
        'categorias': categorias
    })



# Función para obtener marcas
@login_required
def get_marcas(request):
    try:
        marcas = list(Marca.objects.all().values('id', 'Nombre'))
        return JsonResponse({'success': True, 'marcas': marcas})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

# Función para obtener categorías
@login_required
def get_categorias(request):
    try:
        categorias = list(Categoria.objects.all().values('id', 'Nombre'))
        return JsonResponse({'success': True, 'categorias': categorias})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

# Función para obtener proveedores
@login_required
def get_proveedores(request):
    try:
        proveedores = list(Proveedor.objects.all().values('id', 'RazonSocial'))
        return JsonResponse({'success': True, 'proveedores': proveedores})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

# Función para obtener unidades de medida
def get_unidades(request):
    try:
        unidades = list(UnidadDeMedida.objects.all().values('id', 'Nombre'))
        return JsonResponse({'success': True, 'unidades': unidades})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

# Función para obtener datos de un producto
@login_required
def get_producto(request):
    if request.method == 'GET':
        try:
            producto_id = request.GET.get('id')
            if not producto_id:
                return JsonResponse({'success': False, 'error': 'No se proporcionó ID de producto'})
                
            producto = Producto.objects.get(id=producto_id)
            # Convertir el producto a diccionario
            producto_dict = {
                'id': producto.id,
                'Nombre': producto.Nombre,
                'Marca': producto.Marca.id if producto.Marca else None,
                'Categoria': producto.Categoria.id if producto.Categoria else None,
                'CodigoDeBarras': producto.CodigoDeBarras,
                'PrecioCosto': str(producto.PrecioCosto),
                'PrecioDeLista': str(producto.PrecioDeLista),
                'PrecioDeContado': str(producto.PrecioDeContado),
                'Cantidad': producto.Cantidad,
                'CantidadMinimaSugerida': producto.CantidadMinimaSugerida,
                'FechaUltimaModificacion': producto.FechaUltimaModificacion.strftime('%Y-%m-%d') if producto.FechaUltimaModificacion else None,
            }
            return JsonResponse({'success': True, 'producto': producto_dict})
        except Producto.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Producto no encontrado'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Método no permitido'})

# Función para agregar marcas
def add_marca_view(request):
    if request.method == "POST":
        try:
            nombre = request.POST.get('Nombre')
            marca = Marca.objects.create(Nombre=nombre)
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'id': marca.id,
                    'nombre': marca.Nombre,
                    'seleccionar': True  # Indicador para seleccionar la marca
                })
            messages.success(request, "Marca agregada exitosamente.")
        except Exception as e:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': str(e)})
            messages.error(request, f"Error al guardar la marca: {str(e)}")
    return redirect('Productos')

# Función para agregar unidades de medida
def add_unidad_view(request):
    if request.method == "POST":
        try:
            nombre = request.POST.get('Nombre')
            unidad = UnidadDeMedida.objects.create(Nombre=nombre)
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'id': unidad.id,
                    'nombre': unidad.Nombre
                })
            messages.success(request, "Unidad de medida agregada exitosamente.")
        except Exception as e:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': str(e)})
            messages.error(request, f"Error al guardar la unidad de medida: {str(e)}")
    return redirect('Productos')

# Funciones para gestión de compras
@login_required
def compras_view(request):
    context = {}
    # Verificar si hay una caja abierta para este usuario
    caja_abierta = Caja.objects.filter(Cajero=request.user, Estado='ABIERTA').first()
    context['caja_abierta'] = caja_abierta
    
    if request.method == "POST":
        # Solo permitir registro de compras pagadas si hay caja abierta
        estado = request.POST.get('estado', 'PENDIENTE')
        if estado == 'PAGADA' and not caja_abierta:
            return JsonResponse({'success': False, 'error': 'Debe tener una caja abierta para registrar pagos'})
            
        try:
            # Obtener datos del formulario
            proveedor_id = request.POST.get('proveedor')
            fecha = request.POST.get('fecha')
            estado = request.POST.get('estado', 'PENDIENTE')  # Default a 'PENDIENTE'
            medio_pago_id = request.POST.get('medio_pago')
            fecha_pago = request.POST.get('fecha_pago')
            
            # Crear la compra
            compra = Compra.objects.create(
                Fecha=fecha,
                Proveedor_id=proveedor_id,
                ImporteTotal=0,
                Estado=estado.upper(),  # Asegurar que esté en mayúsculas
                Usuario=request.user  # Asignar el usuario actual
            )
            
            # Si la compra está pagada, actualizar medio de pago y fecha
            if estado.upper() == 'PAGADA' and medio_pago_id and fecha_pago:
                compra.MedioDePago_id = medio_pago_id
                compra.FechaPago = fecha_pago
                compra.save()
            
            # Procesar los detalles de la compra
            total = 0
            productos = request.POST.getlist('producto[]')
            cantidades = request.POST.getlist('cantidad[]')
            precios = request.POST.getlist('precio[]')
            
            for producto_id, cantidad, precio in zip(productos, cantidades, precios):
                if producto_id and cantidad and precio:
                    producto = Producto.objects.get(pk=producto_id)
                    cantidad = int(cantidad)
                    precio = float(precio)
                    
                    # Actualizar el precio de costo solo si el nuevo precio es mayor
                    if precio > producto.PrecioCosto:
                        producto.PrecioCosto = precio
                        
                        # Calcular los nuevos precios de venta (30% y 40% de ganancia)
                        precio_lista = precio * 1.30  # 30% de ganancia
                        precio_contado = precio * 1.40  # 40% de ganancia
                        
                        # Actualizar los precios del producto
                        producto.PrecioDeLista = precio_lista
                        producto.PrecioDeContado = precio_contado
                        producto.FechaUltimaModificacion = fecha
                    
                    # Actualizar el stock
                    producto.Cantidad += cantidad
                    producto.save()
                    
                    # Crear el detalle de compra con el precio unitario
                    DetalleCompra.objects.create(
                        Compra=compra,
                        Producto=producto,
                        Cantidad=cantidad,
                        PrecioUnitario=precio
                    )
                    
                    # Registrar movimiento de stock
                    MovimientoStock.objects.create(
                        Fecha=compra.Fecha,
                        Producto=producto,
                        Tipo='ENTRADA',
                        Cantidad=cantidad,
                        StockAnterior=producto.Cantidad - cantidad,
                        StockResultante=producto.Cantidad,
                        OrigenMovimiento='COMPRA',
                        Usuario=request.user,
                        Observaciones=f'Compra #{compra.id}'
                    )
                    
                    total += precio * cantidad
            
            # Actualizar el total de la compra
            compra.ImporteTotal = total
            compra.save()
            
            return JsonResponse({
                'success': True,
                'compra_id': compra.id
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    # Si es GET, mostrar el formulario
    proveedores = Proveedor.objects.all()
    productos = Producto.objects.all()
    medios_pago = MedioDePago.objects.all()
    
    context = {
        'proveedores': proveedores,
        'productos': productos,
        'medios_pago': medios_pago,
    }
    return render(request, 'compras.html', context)

@login_required
def lista_compras(request):
    # Obtener parámetros de filtro
    fecha_desde = request.GET.get('fecha_desde')
    fecha_hasta = request.GET.get('fecha_hasta')
    estado = request.GET.get('estado')
    proveedor = request.GET.get('proveedor')
    producto = request.GET.get('producto')  # Nuevo filtro para producto
    query = request.GET.get('q', '')
    
    # Obtener compras con filtros aplicados
    compras = Compra.objects.all().order_by('-Fecha')
    
    # Aplicar filtros
    if fecha_desde:
        compras = compras.filter(Fecha__gte=fecha_desde)
    if fecha_hasta:
        compras = compras.filter(Fecha__lte=fecha_hasta)
    if estado:
        compras = compras.filter(Estado=estado.upper())
    if proveedor:
        compras = compras.filter(Proveedor_id=proveedor)
    if producto:
        # Filtrar compras que incluyen este producto en los detalles
        compras = compras.filter(detallecompra__Producto_id=producto).distinct()
    if query:
        # Buscar por proveedor, número de compra
        compras = compras.filter(
            models.Q(Proveedor__RazonSocial__icontains=query) |
            models.Q(id__icontains=query)
        )
    
    # Paginación
    paginator = Paginator(compras, 25)  # 25 compras por página
    page = request.GET.get('page')
    try:
        compras_paginadas = paginator.page(page)
    except PageNotAnInteger:
        compras_paginadas = paginator.page(1)
    except EmptyPage:
        compras_paginadas = paginator.page(paginator.num_pages)
    
    # Preparar contexto
    context = {
        'compras': compras_paginadas,
        'proveedores': Proveedor.objects.all(),
        'productos': Producto.objects.all(),  # Para selector de productos
        'medios_pago': MedioDePago.objects.all(),
        # Parámetros de filtro para mantener selecciones
        'fecha_desde': fecha_desde,
        'fecha_hasta': fecha_hasta,
        'estado_filtro': estado,
        'proveedor_filtro': proveedor,
        'producto_filtro': producto,
        'query': query,
        # Total de compras filtradas
        'total_compras': compras.count(),
        'total_monto': compras.aggregate(total=models.Sum('ImporteTotal'))['total'] or 0
    }
    
    return render(request, 'lista_compras.html', context)

def detalles_compra(request):
    try:
        compra_id = request.GET.get('compra_id')
        detalles = DetalleCompra.objects.filter(Compra_id=compra_id)
        
        detalles_json = []
        for detalle in detalles:
            detalles_json.append({
                'producto': detalle.Producto.Nombre,
                'cantidad': detalle.Cantidad,
                'precio_unitario': float(detalle.PrecioUnitario) if detalle.PrecioUnitario else 0
            })
        
        return JsonResponse({
            'success': True,
            'detalles': detalles_json
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

def actualizar_pago_compra(request):
    if request.method == 'POST':
        try:
            compra_id = request.POST.get('compra_id')
            compra = Compra.objects.get(id=compra_id)
            
            # Verificar si hay caja abierta
            caja_abierta = Caja.objects.filter(Cajero=request.user, Estado='ABIERTA').first()
            if not caja_abierta:
                return JsonResponse({
                    'success': False, 
                    'error': 'Debe tener una caja abierta para registrar pagos'
                })
            
            # Usar el formulario para validación
            form_data = {
                'Compra': compra_id,
                'MedioDePago': request.POST.get('medio_pago'),
                'Monto': request.POST.get('monto', compra.ImporteTotal)
            }
            
            form = PagoCompraForm(form_data)
            if form.is_valid():
                pago = form.save(commit=False)  # No guardamos aún
                
                # Actualizar el estado de la compra
                compra.Estado = 'PAGADA'
                compra.MedioDePago_id = request.POST.get('medio_pago')
                compra.FechaPago = request.POST.get('fecha_pago')
                compra.save()
                
                # Ahora sí guardamos el pago
                pago.save()
                
                return JsonResponse({'success': True})
            else:
                return JsonResponse({'success': False, 'error': 'Datos inválidos', 'form_errors': form.errors})
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})

def registrar_pago(request):
    if request.method == 'POST':
        try:
            medio_pago_id = request.POST.get('medio_pago')
            fecha_pago = request.POST.get('fecha_pago')
            
            # Solo validamos que los datos del pago sean correctos
            if not medio_pago_id or not fecha_pago:
                return JsonResponse({
                    'success': False,
                    'error': 'Debe completar todos los campos del pago'
                })
            
            return JsonResponse({
                'success': True,
                'message': 'Datos de pago validados correctamente'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({
        'success': False,
        'error': 'Método no permitido'
    })

def editar_compra(request):
    if request.method == 'POST':
        try:
            compra_id = request.POST.get('compra_id')
            compra = Compra.objects.get(id=compra_id)
            
            # Guardar los detalles antiguos para actualizar el stock
            detalles_antiguos = {detalle.Producto_id: detalle.Cantidad for detalle in DetalleCompra.objects.filter(Compra=compra)}
            
            # Actualizar datos básicos de la compra
            compra.Fecha = request.POST.get('fecha')
            compra.Proveedor_id = request.POST.get('proveedor')
            compra.Estado = request.POST.get('estado')
            
            # Si está pagada, actualizar datos de pago
            if compra.Estado == 'PAGADA':
                compra.MedioDePago_id = request.POST.get('medio_pago')
                compra.FechaPago = request.POST.get('fecha_pago')
            
            # Eliminar detalles antiguos
            DetalleCompra.objects.filter(Compra=compra).delete()
            
            # Procesar nuevos detalles
            total = 0
            productos = request.POST.getlist('producto[]')
            cantidades = request.POST.getlist('cantidad[]')
            precios = request.POST.getlist('precio[]')
            
            productos_actualizados = []
            
            for producto_id, cantidad, precio in zip(productos, cantidades, precios):
                if producto_id and cantidad and precio:
                    producto = Producto.objects.get(pk=producto_id)
                    cantidad = int(cantidad)
                    precio = float(precio)
                    
                    # Restar la cantidad antigua del stock
                    cantidad_antigua = detalles_antiguos.get(int(producto_id), 0)
                    producto.Cantidad -= cantidad_antigua
                    
                    # Sumar la nueva cantidad
                    producto.Cantidad += cantidad
                    
                    # Actualizar el precio de costo solo si el nuevo precio es mayor
                    if precio > producto.PrecioCosto:
                        producto.PrecioCosto = precio
                        # Calcular los nuevos precios de venta
                        precio_lista = precio * 1.30
                        precio_contado = precio * 1.40
                        
                        # Actualizar los precios del producto
                        producto.PrecioDeLista = precio_lista
                        producto.PrecioDeContado = precio_contado
                        producto.FechaUltimaModificacion = compra.Fecha
                    
                    producto.save()
                    
                    # Agregar información del producto actualizado
                    productos_actualizados.append({
                        'nombre': producto.Nombre,
                        'stock_actual': producto.Cantidad
                    })
                    
                    # Crear el nuevo detalle con el precio unitario
                    DetalleCompra.objects.create(
                        Compra=compra,
                        Producto=producto,
                        Cantidad=cantidad,
                        PrecioUnitario=precio
                    )
                    
                    # Registrar movimiento de stock
                    MovimientoStock.objects.create(
                        Fecha=compra.Fecha,
                        Producto=producto,
                        Tipo='ENTRADA',
                        Cantidad=cantidad,
                        StockAnterior=producto.Cantidad - cantidad,
                        StockResultante=producto.Cantidad,
                        OrigenMovimiento='COMPRA',
                        Usuario=request.user,
                        Observaciones=f'Compra #{compra.id}'
                    )
                    
                    total += precio * cantidad
            
            # Actualizar el total de la compra
            compra.ImporteTotal = total
            compra.save()
            
            return JsonResponse({
                'success': True,
                'stock_actualizado': True,
                'productos_actualizados': productos_actualizados
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})

def obtener_detalles_compra(request):
    try:
        compra_id = request.GET.get('compra_id')
        if not compra_id:
            return JsonResponse({
                'success': False,
                'error': 'No se proporcionó ID de compra'
            })

        compra = Compra.objects.get(id=compra_id)
        detalles = DetalleCompra.objects.filter(Compra=compra)
        
        detalles_json = []
        for detalle in detalles:
            detalles_json.append({
                'producto_id': detalle.Producto.id,
                'cantidad': detalle.Cantidad,
                'precio_unitario': float(detalle.PrecioUnitario) if detalle.PrecioUnitario else 0
            })
        
        return JsonResponse({
            'success': True,
            'compra': {
                'fecha': compra.Fecha.strftime('%Y-%m-%d'),
                'proveedor_id': compra.Proveedor.id,
                'estado': compra.Estado,
                'medio_pago_id': compra.MedioDePago.id if compra.MedioDePago else None,
                'fecha_pago': compra.FechaPago.strftime('%Y-%m-%d') if compra.FechaPago else None
            },
            'detalles': detalles_json
        })
    except Compra.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'La compra no existe'
        })
    except Exception as e:
        print(f"Error en obtener_detalles_compra: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'Error al obtener los detalles: {str(e)}'
        })

def eliminar_compra(request):
    if request.method == 'POST':
        try:
            import json
            data = json.loads(request.body)
            compra_id = data.get('compra_id')
            compra = Compra.objects.get(id=compra_id)
            
            # Si la compra estaba pagada, revertir movimiento de caja
            if compra.Estado == 'PAGADA':
                # Verificar si hay caja abierta
                caja_abierta = Caja.objects.filter(Cajero=request.user, Estado='ABIERTA').first()
                if not caja_abierta:
                    return JsonResponse({
                        'success': False, 
                        'error': 'Debe tener una caja abierta para eliminar compras pagadas'
                    })
                
                # Buscar el movimiento de caja relacionado y eliminarlo
                movimiento = MovimientoCaja.objects.filter(Compra=compra).first()
                if movimiento:
                    # Revertir el saldo
                    caja_abierta.Saldo += compra.ImporteTotal
                    caja_abierta.save()
                    
                    # Eliminar el movimiento
                    movimiento.delete()
            
            # Obtener los detalles de la compra antes de eliminarla
            detalles = DetalleCompra.objects.filter(Compra=compra)
            productos_actualizados = []
            
            # Actualizar el stock de cada producto
            for detalle in detalles:
                producto = detalle.Producto
                # Restar la cantidad del stock ya que se está eliminando la compra
                producto.Cantidad -= detalle.Cantidad
                producto.save()
                productos_actualizados.append({
                    'nombre': producto.Nombre,
                    'stock_actual': producto.Cantidad
                })
            
            # Eliminar la compra
            compra.delete()
            
            return JsonResponse({
                'success': True,
                'stock_actualizado': True,
                'productos_actualizados': productos_actualizados
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})

def delete_subcategoria_view(request):
    if request.method == "POST":
        try:
            subcategoria_id = request.POST.get('subcategoria_id')
            subcategoria = SubCategoria.objects.get(pk=subcategoria_id)
            subcategoria.delete()
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': 'Subcategoría eliminada correctamente'
                })
            messages.success(request, "Subcategoría eliminada exitosamente.")
        except SubCategoria.DoesNotExist:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': 'La subcategoría no existe'
                })
            messages.error(request, "La subcategoría no existe")
        except Exception as e:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': f'Error al eliminar la subcategoría: {str(e)}'
                })
            messages.error(request, f"Error al eliminar la subcategoría: {str(e)}")
    return redirect('Categorias')

@login_required
def imprimir_ticket_view(request, venta_id):
    try:
        # Obtener la venta
        venta = Venta.objects.get(id=venta_id)
        detalles = DetalleVenta.objects.filter(Venta=venta)
        pagos = PagoVenta.objects.filter(Venta=venta)
        
        # Obtener información de la empresa desde settings
        empresa = {
            'nombre': getattr(settings, 'EMPRESA_NOMBRE', 'Mi Empresa'),
            'direccion': getattr(settings, 'EMPRESA_DIRECCION', 'Dirección de la Empresa'),
            'telefono': getattr(settings, 'EMPRESA_TELEFONO', 'Tel: 123-456-7890')
        }
        
        # Preparar el contexto
        context = {
            'venta': venta,
            'detalles': detalles,
            'pagos': pagos,
            'empresa': empresa,
            'fecha': venta.Fecha.strftime('%d/%m/%Y %H:%M')
        }
        
        # Renderizar el template HTML
        return render(request, 'ticket.html', context)
        
    except Venta.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'No se encontró la venta especificada'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

def obtener_pagos_compra(request):
    compra_id = request.GET.get('compra_id')
    
    try:
        compra = Compra.objects.get(id=compra_id)
        
        # Si todavía no existe el modelo PagoCompra, devolvemos datos básicos
        try:
            from ventas.models import PagoCompra
            pagos = PagoCompra.objects.filter(Compra=compra).order_by('-Fecha')
            
            pagos_data = []
            for pago in pagos:
                pagos_data.append({
                    'id': pago.id,
                    'fecha': pago.Fecha.strftime('%d/%m/%Y %H:%M'),
                    'medio_pago': pago.MedioDePago.Nombre,
                    'monto': str(pago.Monto)
                })
                
            total_pagado = compra.get_total_pagado() if hasattr(compra, 'get_total_pagado') else 0
            saldo_pendiente = compra.get_saldo_pendiente() if hasattr(compra, 'get_saldo_pendiente') else compra.ImporteTotal
            
        except (ImportError, AttributeError):
            # Si no existe el modelo PagoCompra aún
            pagos_data = []
            total_pagado = 0
            saldo_pendiente = compra.ImporteTotal
        
        return JsonResponse({
            'success': True,
            'importe_total': str(compra.ImporteTotal),
            'total_pagado': str(total_pagado),
            'saldo_pendiente': str(saldo_pendiente),
            'pagos': pagos_data
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
def ajuste_stock_view(request):
    if request.method == 'POST':
        try:
            id_producto = request.POST.get('id_producto')
            tipo_movimiento = request.POST.get('tipo_movimiento')
            cantidad = Decimal(request.POST.get('cantidad', 0))
            motivo = request.POST.get('motivo')

            if not all([id_producto, tipo_movimiento, cantidad, motivo]):
                return JsonResponse({'success': False, 'error': 'Faltan datos requeridos'})

            producto = Producto.objects.get(id=id_producto)
            stock_anterior = producto.Cantidad

            # Actualizar el stock del producto
            if tipo_movimiento == 'ENTRADA':
                producto.Cantidad += cantidad
            else:  # SALIDA
                if producto.Cantidad < cantidad:
                    return JsonResponse({'success': False, 'error': 'No hay suficiente stock disponible'})
                producto.Cantidad -= cantidad

            # Crear el movimiento de stock
            movimiento = MovimientoStock.objects.create(
                Producto=producto,
                Tipo=tipo_movimiento,
                Cantidad=cantidad,
                StockAnterior=stock_anterior,
                StockResultante=producto.Cantidad,
                OrigenMovimiento='AJUSTE',
                Usuario=request.user,
                Observaciones=motivo
            )

            # Guardar los cambios en una transacción
            with transaction.atomic():
                movimiento.save()
                producto.save()

            return JsonResponse({'success': True})
        except Producto.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Producto no encontrado'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    else:
        # Si es GET, mostrar el formulario de ajuste
        form = MovimientoStockForm()
        context = {
            'form': form,
            'titulo': 'Ajuste de Stock'
        }
        return render(request, 'ventas/ajuste_stock.html', context)

@login_required
def dashboard_view(request):
    # Obtener fechas del request o usar valores por defecto
    fecha_desde = request.GET.get('fecha_desde', (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'))
    fecha_hasta = request.GET.get('fecha_hasta', datetime.now().strftime('%Y-%m-%d'))

    # Convertir fechas a objetos datetime
    fecha_desde = datetime.strptime(fecha_desde, '%Y-%m-%d')
    fecha_hasta = datetime.strptime(fecha_hasta, '%Y-%m-%d') + timedelta(days=1)

    # Obtener ventas del período
    ventas = Venta.objects.filter(
        Fecha__range=[fecha_desde, fecha_hasta]
    )

    # Calcular totales
    total_ventas = {
        'total': float(ventas.aggregate(total=Sum('ImporteTotal'))['total'] or 0),
        'cantidad': ventas.count()
    }

    # Obtener ventas diarias para el gráfico y formatear las fechas
    ventas_diarias = []
    for venta in ventas.values('Fecha__date').annotate(
        total=Sum('ImporteTotal')
    ).order_by('Fecha__date'):
        ventas_diarias.append({
            'Fecha__date': venta['Fecha__date'].strftime('%Y-%m-%d'),
            'total': float(venta['total'])
        })

    # Obtener productos con stock bajo
    productos_stock_bajo = Producto.objects.filter(
        Cantidad__lte=F('CantidadMinimaSugerida')
    )

    # Obtener productos con más salidas
    productos_mas_salidas = MovimientoStock.objects.filter(
        Fecha__range=[fecha_desde, fecha_hasta],
        Tipo='SALIDA'
    ).values(
        'Producto__Nombre'
    ).annotate(
        total_salidas=Sum('Cantidad')
    ).order_by('-total_salidas')[:10]

    # Agregar información de stock actual y mínimo a los productos con más salidas
    for producto in productos_mas_salidas:
        producto_obj = Producto.objects.get(Nombre=producto['Producto__Nombre'])
        producto['stock_actual'] = producto_obj.Cantidad
        producto['stock_minimo'] = producto_obj.CantidadMinimaSugerida

    # Obtener resumen de movimientos de stock
    movimientos_stock = MovimientoStock.objects.filter(
        Fecha__range=[fecha_desde, fecha_hasta]
    ).values('Tipo').annotate(
        cantidad=Count('id')
    )
    
    context = {
        'fecha_desde': fecha_desde,
        'fecha_hasta': fecha_hasta - timedelta(days=1),
        'total_ventas': total_ventas,
        'ventas_diarias': ventas_diarias,
        'productos_stock_bajo': productos_stock_bajo,
        'productos_mas_salidas': productos_mas_salidas,
        'movimientos_stock': movimientos_stock,
    }
    
    return render(request, 'ventas/dashboard.html', context)

def informe_costos_ganancias(request):
    # Obtener fechas del filtro o usar el mes actual
    fecha_desde = request.GET.get('fecha_desde')
    fecha_hasta = request.GET.get('fecha_hasta')
    
    if not fecha_desde or not fecha_hasta:
        # Si no hay fechas, usar el mes actual
        hoy = datetime.now()
        fecha_desde = hoy.replace(day=1).strftime('%Y-%m-%d')
        fecha_hasta = (hoy.replace(day=1) + timedelta(days=32)).replace(day=1).strftime('%Y-%m-%d')
    
    # Convertir fechas a datetime
    fecha_desde = datetime.strptime(fecha_desde, '%Y-%m-%d')
    fecha_hasta = datetime.strptime(fecha_hasta, '%Y-%m-%d')
    
    # Obtener ventas del período
    ventas_periodo = Venta.objects.filter(
        Fecha__range=[fecha_desde, fecha_hasta]
    ).aggregate(
        total=Coalesce(Sum('ImporteTotal'), 0, output_field=DecimalField()),
        cantidad=Count('id')
    )
    
    # Obtener costos de productos vendidos
    costos_productos = DetalleVenta.objects.filter(
        Venta__Fecha__range=[fecha_desde, fecha_hasta]
    ).aggregate(
        costo_total=Coalesce(Sum(F('Cantidad') * F('Producto__PrecioCosto')), 0, output_field=DecimalField())
    )
    
    # Obtener compras del período
    compras_periodo = Compra.objects.filter(
        Fecha__range=[fecha_desde, fecha_hasta]
    ).aggregate(
        total=Coalesce(Sum('ImporteTotal'), 0, output_field=DecimalField()),
        cantidad=Count('id')
    )
    
    # Calcular ganancia bruta (ventas - costos de productos)
    ganancia_bruta = float(ventas_periodo['total'] or 0) - float(costos_productos['costo_total'] or 0)
    
    # Calcular ganancia neta (ventas - costos de productos - compras)
    ganancia_neta = ganancia_bruta - float(compras_periodo['total'] or 0)
    
    # Calcular porcentajes
    ganancia_bruta_porcentaje = (ganancia_bruta / float(ventas_periodo['total'] or 1)) * 100 if ventas_periodo['total'] else 0
    ganancia_neta_porcentaje = (ganancia_neta / float(ventas_periodo['total'] or 1)) * 100 if ventas_periodo['total'] else 0
    
    context = {
        'fecha_desde': fecha_desde,
        'fecha_hasta': fecha_hasta,
        'ventas_periodo': ventas_periodo,
        'costos_productos': costos_productos,
        'compras_periodo': compras_periodo,
        'ganancia_bruta': ganancia_bruta,
        'ganancia_neta': ganancia_neta,
        'ganancia_bruta_porcentaje': ganancia_bruta_porcentaje,
        'ganancia_neta_porcentaje': ganancia_neta_porcentaje,
    }
    
    return render(request, 'ventas/informe_costos_ganancias.html', context)

@login_required
def verificar_marca(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        existe = Marca.objects.filter(Nombre__iexact=nombre).exists()
        return JsonResponse({'existe': existe})
    return JsonResponse({'error': 'Método no permitido'}, status=405)

@csrf_exempt
def verificar_categoria(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        if nombre:
            # Buscar si existe una categoría con el mismo nombre (ignorando mayúsculas/minúsculas)
            existe = Categoria.objects.filter(Nombre__iexact=nombre).exists()
            return JsonResponse({'existe': existe})
    return JsonResponse({'error': 'Método no permitido'}, status=405)


from escpos.printer import Win32Raw

def imprimir_ticket_en_pos58(venta, detalles, pagos):
    try:
        from escpos.printer import Network
        from escpos.exceptions import USBNotFoundError
        
        try:
            # Inicializar la impresora usando el nombre
            p = Network("POS-58")
            
            # Configurar el tamaño de fuente y alineación
            p.set(align='center', font='a', width=1, height=1)
            
            # Imprimir encabezado
            p.text("\n")
            p.text("{{ empresa.nombre }}\n")
            p.text("{{ empresa.direccion }}\n")
            p.text("Tel: {{ empresa.telefono }}\n")
            p.text("\n")
            
            # Línea separadora
            p.text("-" * 32 + "\n")
            
            # Información del ticket
            p.set(align='center')
            p.text("TICKET DE VENTA\n")
            p.text(f"N° {venta.NumeroComprobate}\n")
            p.text(f"Fecha: {venta.Fecha.strftime('%d/%m/%Y %H:%M')}\n")
            
            # Línea separadora
            p.text("-" * 32 + "\n")
            
            # Tabla de productos
            p.set(align='left')
            p.text("Descripción".ljust(20) + "Cant".rjust(4) + "Subtotal".rjust(8) + "\n")
            p.text("-" * 32 + "\n")
            
            for detalle in detalles:
                nombre = detalle.Producto.Nombre[:20].ljust(20)
                cantidad = str(detalle.Cantidad).rjust(4)
                subtotal = f"${detalle.Subtotal:.2f}".rjust(8)
                p.text(f"{nombre}{cantidad}{subtotal}\n")
            
            # Línea separadora
            p.text("-" * 32 + "\n")
            
            # Total
            p.set(align='right')
            p.text(f"TOTAL: ${venta.ImporteTotal:.2f}\n")
            
            # Formas de pago
            p.set(align='left')
            p.text("\nFormas de Pago:\n")
            for pago in pagos:
                medio = pago.MedioDePago.Nombre[:14].ljust(14)
                monto = f"${pago.Monto:.2f}".rjust(8)
                p.text(f"{medio}{monto}\n")
            
            # Pie de página
            p.text("\n")
            p.set(align='center')
            p.text("¡Gracias por su compra!\n")
            p.text("Conserve este ticket para\n")
            p.text("cualquier reclamo\n")
            
            # Cortar el papel
            p.cut()
            
        except Exception as e:
            print(f"Error al imprimir: {e}")
        finally:
            # Cerrar la conexión con la impresora
            if 'p' in locals():
                p.close()
                
    except Exception as e:
        print(f"Error al imprimir el ticket: {e}")

@staff_member_required
@csrf_exempt
def forzar_cierre_caja_view(request, caja_id):
    """Vista para forzar el cierre de una caja (solo para superusuarios)"""
    if request.method == 'POST':
        try:
            caja = Caja.objects.get(id=caja_id, Estado='ABIERTA')
            
            # Calcular el saldo final según el sistema
            saldo_inicial = caja.SaldoInicial
            total_efectivo = caja.GetTotalEfectivo()
            saldo_final_sistema = saldo_inicial + total_efectivo
            
            # Forzar el cierre con el saldo del sistema como saldo real
            caja.CerrarCaja(
                saldo_final_real=saldo_final_sistema,
                observaciones="Cierre forzado por administrador"
            )
            
            return JsonResponse({
                'success': True,
                'message': 'Caja cerrada exitosamente'
            })
            
        except Caja.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'La caja no existe o ya está cerrada'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({
        'success': False,
        'error': 'Método no permitido'
    })




