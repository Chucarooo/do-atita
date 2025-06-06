from django.urls import path
from . import views

urlpatterns = [
    path('', views.index_view, name='Index'),
    path('clientes/', views.clientes_view, name='Clientes'),
    path('add_cliente/', views.add_cliente_view, name='AddCliente'),
    path('edit_cliente/', views.edit_cliente_view, name='EditCliente'),
    path('delete_cliente/', views.delete_cliente_view, name='DeleteCliente'),
    path('proveedores/', views.proveedores_view, name='Proveedores'),
    path('add_proveedor/', views.add_proveedor_view, name='AddProveedor'),
    path('edit_proveedor/', views.edit_proveedor_view, name='EditProveedor'),
    path('delete_proveedor/', views.delete_proveedor_view, name='DeleteProveedor'),
    path('productos/', views.productos_view, name='Productos'),
    path('add_producto/', views.add_producto_view, name='AddProducto'),
    path('edit_producto/', views.EditProducto, name='EditProducto'),
    path('delete_producto/', views.delete_producto_view, name='DeleteProducto'),
    path('categorias/', views.categorias_view, name='Categorias'),
    path('add_categoria/', views.add_categoria_view, name='AddCategoria'),
    path('edit_categoria/', views.edit_categoria_view, name='EditCategoria'),
    path('delete_categoria/', views.delete_categoria_view, name='DeleteCategoria'),
    path('login/', views.login_view, name='Login'),
    path('logout/', views.logout_view, name='Logout'),
    path('register/', views.register_view, name='Register'),
    path('caja/', views.caja_view, name='caja'),
    path('apertura_caja/', views.caja_view, name='apertura_caja'),
    path('ventas/', views.ventas_view, name='ventas'),
    path('ventas/imprimir_ticket/<int:venta_id>/', views.imprimir_ticket_view, name='imprimir_ticket'),
    path('historial-cajas/', views.historial_cajas_view, name='historial_cajas'),
    path('detalle-caja/<int:caja_id>/', views.detalle_caja_view, name='detalle_caja'),
    path('forzar-cierre-caja/<int:caja_id>/', views.forzar_cierre_caja_view, name='forzar_cierre_caja'),
    path('guardar-cliente-ajax/', views.guardar_cliente_ajax, name='guardar_cliente_ajax'),
    path('historial-movimientos/', views.historial_movimientos, name='historial_movimientos'),
    path('ajustes/', views.lista_ajustes, name='lista_ajustes'),
    path('ajustes/crear/', views.crear_ajuste, name='crear_ajuste'),
    path('ajustes/<int:ajuste_id>/', views.detalle_ajuste, name='detalle_ajuste'),
    path('inventarios/', views.lista_inventarios, name='lista_inventarios'),
    path('inventarios/crear/', views.crear_inventario, name='crear_inventario'),
    path('inventarios/<int:inventario_id>/', views.detalle_inventario, name='detalle_inventario'),
    path('transferencias/', views.lista_transferencias, name='lista_transferencias'),
    path('transferencias/crear/', views.crear_transferencia, name='crear_transferencia'),
    path('transferencias/<int:transferencia_id>/completar/', views.completar_transferencia, name='completar_transferencia'),
    path('transferencias/<int:transferencia_id>/cancelar/', views.cancelar_transferencia, name='cancelar_transferencia'),
    path('reservas/', views.lista_reservas, name='lista_reservas'),
    path('reservas/crear/', views.crear_reserva, name='crear_reserva'),
    path('reservas/<int:reserva_id>/cancelar/', views.cancelar_reserva, name='cancelar_reserva'),
    path('reservas/<int:reserva_id>/utilizar/', views.utilizar_reserva, name='utilizar_reserva'),
    
    # URLs para gestión de compras
    path('compras/', views.compras_view, name='compras'),
    path('lista-compras/', views.lista_compras, name='lista_compras'),
    path('add_marca/', views.add_marca_view, name='add_marca'),
    path('verificar_marca/', views.verificar_marca, name='verificar_marca'),
    path('verificar_categoria/', views.verificar_categoria, name='verificar_categoria'),
    path('detalles-compra/', views.detalles_compra, name='detalles_compra'),
    path('actualizar-pago-compra/', views.actualizar_pago_compra, name='actualizar_pago_compra'),
    path('registrar-pago/', views.registrar_pago, name='registrar_pago'),
    path('compras/editar/', views.editar_compra, name='editar_compra'),
    path('compras/obtener-detalles/', views.obtener_detalles_compra, name='obtener_detalles_compra'),
    path('compras/eliminar/', views.eliminar_compra, name='eliminar_compra'),
    
    # Endpoints para obtener datos mediante AJAX
    path('get_marcas/', views.get_marcas, name='get_marcas'),
    path('get_categorias/', views.get_categorias, name='get_categorias'),
    path('get_proveedores/', views.get_proveedores, name='get_proveedores'),
    path('get_unidades/', views.get_unidades, name='get_unidades'),
    path('get_producto/', views.get_producto, name='get_producto'),
    path('add_unidad/', views.add_unidad_view, name='AddUnidad'),
    path('delete_subcategoria/', views.delete_subcategoria_view, name='DeleteSubcategoria'),
    path('obtener-pagos-compra/', views.obtener_pagos_compra, name='obtener_pagos_compra'),

    # URLs para Movimientos de Stock
    path('movimientos/', views.historial_movimientos, name='historial_movimientos'),
    path('movimientos/ajuste/', views.ajuste_stock_view, name='ajuste_stock'),

    # URLs para Dashboard
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('informe-costos-ganancias/', views.informe_costos_ganancias, name='informe_costos_ganancias'),
]