import os
import django
import random
from faker import Faker
from .models import *

fake = Faker('es_ES')
cantidad_registros = 10
def generar_clientes(N=cantidad_registros):
    fake = Faker('es_ES')
    for _ in range(N):
        nombre = fake.first_name()
        apellido = fake.last_name()
        dni = fake.unique.random_number(digits=8, fix_len=True)
        tel = fake.phone_number()
        email = fake.email()
        direccion = fake.address()
        Cliente.objects.create(
            Nombre=nombre,
            Apellido=apellido,
            DNI=dni,
            Tel=tel,
            Email=email,
            Direccion=direccion
        )


def generar_proveedores(N=cantidad_registros):
    fake = Faker('es_ES')
    for _ in range(N):
        razonSocial = fake.first_name()
        cuit = fake.unique.random_number(digits=8, fix_len=True)
        tel = fake.phone_number()
        email = fake.email()
        direccion = fake.address()
        Proveedor.objects.create(
            RazonSocial=razonSocial,
            CUIT=cuit,
            Tel=tel,
            Email=email,
            Direccion=direccion
        )

def generar_categorias(N=cantidad_registros):
    for _ in range(N):
        nombre = fake.word()
        Categoria.objects.create(Nombre=nombre)

def generar_subcategorias(N=cantidad_registros):
    categorias = list(Categoria.objects.all())
    for _ in range(N):
        nombre = fake.word()
        categoria = random.choice(categorias)
        SubCategoria.objects.create(Nombre=nombre, Categoria=categoria)

def generar_marcas(N=cantidad_registros):
    for _ in range(N):
        nombre = fake.word()
        Marca.objects.create(Nombre=nombre)

def generar_unidades_de_medida(N=cantidad_registros):
    for _ in range(N):
        nombre = fake.word()
        UnidadDeMedida.objects.create(Nombre=nombre)

def generar_productos(N=cantidad_registros):
    subcategorias = list(SubCategoria.objects.all())
    marcas = list(Marca.objects.all())
    proveedores = list(Proveedor.objects.all())
    unidades_de_medida = list(UnidadDeMedida.objects.all())
    for _ in range(N):
        nombre = fake.word()
        subcategoria = random.choice(subcategorias)
        marca = random.choice(marcas)
        proveedor = random.choice(proveedores)
        codigo_de_barras = fake.unique.ean13()
        descripcion = fake.text(max_nb_chars=200)
        cantidad = fake.pydecimal(left_digits=5, right_digits=2, positive=True)
        cantidad_minima_sugerida = fake.pydecimal(left_digits=2, right_digits=2, positive=True)
        unidad_de_medida = random.choice(unidades_de_medida)
        precio_costo = fake.pydecimal(left_digits=5, right_digits=2, positive=True)
        precio_de_lista = fake.pydecimal(left_digits=5, right_digits=2, positive=True)
        precio_de_contado = fake.pydecimal(left_digits=5, right_digits=2, positive=True)
        fecha_ultima_modificacion = fake.date_this_year()
        Producto.objects.create(
            Nombre=nombre,
            SubCategoria=subcategoria,
            Marca=marca,
            Proveedor=proveedor,
            CodigoDeBarras=codigo_de_barras,
            Descripcion=descripcion,
            Cantidad=cantidad,
            CantidadMinimaSugerida=cantidad_minima_sugerida,
            UnidadDeMedida=unidad_de_medida,
            PrecioCosto=precio_costo,
            PrecioDeLista=precio_de_lista,
            PrecioDeContado=precio_de_contado,
            FechaUltimaModificacion=fecha_ultima_modificacion
        )

def generar_medios_de_pago(N=cantidad_registros):
    for _ in range(N):
        nombre = fake.word()
        MedioDePago.objects.create(Nombre=nombre)

def generar_ventas(N=cantidad_registros):
    clientes = list(Cliente.objects.all())
    medios_de_pago = list(MedioDePago.objects.all())
    productos = list(Producto.objects.all())
    for _ in range(N):
        fecha = fake.date_this_year()
        numero_comprobante = fake.unique.random_number(digits=10, fix_len=True)
        cliente = random.choice(clientes)
        medio_de_pago = random.choice(medios_de_pago)
        importe_total = fake.pydecimal(left_digits=5, right_digits=2, positive=True)
        venta = Venta.objects.create(
            Fecha=fecha,
            NumeroComprobate=numero_comprobante,
            Cliente=cliente,
            MedioDePago=medio_de_pago,
            ImporteTotal=importe_total
        )
        for _ in range(random.randint(1, 5)):
            producto = random.choice(productos)
            cantidad = random.randint(1, 10)
            DetalleVenta.objects.create(Venta=venta, Producto=producto, Cantidad=cantidad)

def generar_presupuestos(N=cantidad_registros):
    clientes = list(Cliente.objects.all())
    medios_de_pago = list(MedioDePago.objects.all())
    productos = list(Producto.objects.all())
    for _ in range(N):
        fecha = fake.date_this_year()
        cliente = random.choice(clientes)
        medio_de_pago = random.choice(medios_de_pago)
        importe_total = fake.pydecimal(left_digits=5, right_digits=2, positive=True)
        presupuesto = Presupuesto.objects.create(
            Fecha=fecha,
            Cliente=cliente,
            MedioDePago=medio_de_pago,
            ImporteTotal=importe_total
        )
        for _ in range(random.randint(1, 5)):
            producto = random.choice(productos)
            cantidad = random.randint(1, 10)
            DetallePresupuesto.objects.create(Presupuesto=presupuesto, Producto=producto, Cantidad=cantidad)

def generar_compras(N=cantidad_registros):
    proveedores = list(Proveedor.objects.all())
    productos = list(Producto.objects.all())
    for _ in range(N):
        fecha = fake.date_this_year()
        proveedor = random.choice(proveedores)
        importe_total = fake.pydecimal(left_digits=5, right_digits=2, positive=True)
        compra = Compra.objects.create(
            Fecha=fecha,
            Proveedor=proveedor,
            ImporteTotal=importe_total
        )
        for _ in range(random.randint(1, 5)):
            producto = random.choice(productos)
            cantidad = random.randint(1, 10)
            DetalleCompra.objects.create(Compra=compra, Producto=producto, Cantidad=cantidad)

def generar_cuentas(N=cantidad_registros):
    clientes = list(Cliente.objects.all())
    productos = list(Producto.objects.all())
    for _ in range(N):
        cliente = random.choice(clientes)
        fecha_de_alta = fake.date_this_year()
        fecha_de_ultima_modificacion = fake.date_this_year()
        importe_total = fake.pydecimal(left_digits=5, right_digits=2, positive=True)
        cuenta = Cuenta.objects.create(
            Cliente=cliente,
            FechaDeAlta=fecha_de_alta,
            FechaDeUltimaModificacion=fecha_de_ultima_modificacion,
            ImporteTotal=importe_total
        )
        for _ in range(random.randint(1, 5)):
            producto = random.choice(productos)
            cantidad = random.randint(1, 10)
            DetalleCuenta.objects.create(Cuenta=cuenta, Producto=producto, Cantidad=cantidad)