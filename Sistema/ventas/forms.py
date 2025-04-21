from django import forms
from .models import Proveedor, Cliente, Producto, Categoria, Venta, PagoVenta, MovimientoStock
from .models import PagoCompra, Compra
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class AddClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['Nombre', 'Apellido', 'DNI', 'Telefono', 'Email', 'Direccion']
        labels = {
            'Nombre': 'Nombre',
            'Apellido': 'Apellido',
            'DNI': 'DNI',
            'Telefono': 'Teléfono',
            'Email': 'Email',
            'Direccion': 'Dirección',
        }

class EditClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['Nombre', 'Apellido', 'DNI', 'Telefono', 'Email', 'Direccion']
        labels = {
            'Nombre': 'Nombre:',
            'Apellido': 'Apellido:',
            'DNI': 'DNI:',
            'Telefono': 'Teléfono:',
            'Email': 'Email:',
            'Direccion': 'Dirección:',
        }
        widgets = {
            'Nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '', 'id': 'nombre_editar'}),
            'Apellido': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '', 'id': 'apellido_editar'}),
            'DNI': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '', 'id': 'dni_editar'}),
            'Telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '', 'id': 'telefono_editar'}),
            'Email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': '', 'id': 'email_editar'}),
            'Direccion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '', 'id': 'direccion_editar'}),
        }

class AddProveedorForm(forms.ModelForm):
    class Meta:
        model = Proveedor
        fields = ['RazonSocial', 'CUIT', 'Tel', 'Email', 'Direccion']
        labels = {
            'RazonSocial': 'Razón Social',
            'CUIT': 'CUIT',
            'Tel': 'Teléfono',
            'Email': 'Email',
            'Direccion': 'Dirección',
        }

class EditProveedorForm(forms.ModelForm):
    class Meta:
        model = Proveedor
        fields = ['RazonSocial', 'CUIT', 'Tel', 'Email', 'Direccion']
        labels = {
            'RazonSocial': 'Razón Social:',
            'CUIT': 'CUIT:',
            'Tel': 'Teléfono:',
            'Email': 'Email:',
            'Direccion': 'Dirección:',
        }

class AddProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = [
            'Nombre', 'Categoria', 'Marca', 'CodigoDeBarras',
            'Cantidad', 'CantidadMinimaSugerida', 'PrecioCosto', 'PrecioDeLista',
            'PrecioDeContado'
        ]
        labels = {
            'Nombre': 'Nombre del Producto',
            'Categoria': 'Categoría',
            'Marca': 'Marca',
            'CodigoDeBarras': 'Código de Barras',
            'Cantidad': 'Cantidad en Stock',
            'CantidadMinimaSugerida': 'Cantidad Mínima Sugerida',
            'UnidadDeMedida': 'Unidad de Medida',
            'PrecioCosto': 'Precio de Costo',
            'PrecioDeLista': 'Precio de Lista',
            'PrecioDeContado': 'Precio de Contado',
        }
        widgets = {
            'Categoria': forms.Select(attrs={'class': 'form-control'}),
        }

class EditProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = [
            'Nombre', 'Categoria', 'Marca', 'CodigoDeBarras',
            'Cantidad', 'CantidadMinimaSugerida', 'PrecioCosto', 'PrecioDeLista',
            'PrecioDeContado'
        ]
        labels = {
            'Nombre': 'Nombre del Producto:',
            'Categoria': 'Categoría:',
            'Marca': 'Marca:',
            'Proveedor': 'Proveedor:',
            'CodigoDeBarras': 'Código de Barras:',
            'Descripcion': 'Descripción:',
            'Cantidad': 'Cantidad en Stock:',
            'CantidadMinimaSugerida': 'Cantidad Mínima Sugerida:',
            'UnidadDeMedida': 'Unidad de Medida:',
            'PrecioCosto': 'Precio de Costo:',
            'PrecioDeLista': 'Precio de Lista:',
            'PrecioDeContado': 'Precio de Contado:',
        }
        widgets = {
            'Nombre': forms.TextInput(attrs={'type': 'text', 'placeholder': 'Editar nombre del producto'}),
            'Categoria': forms.Select(attrs={'placeholder': 'Editar categoría'}),
            'Marca': forms.Select(attrs={'placeholder': 'Editar marca'}),
            'Proveedor': forms.Select(attrs={'placeholder': 'Editar proveedor'}),
            'CodigoDeBarras': forms.TextInput(attrs={'type': 'text', 'placeholder': 'Editar código de barras'}),
            'Descripcion': forms.Textarea(attrs={'placeholder': 'Editar descripción', 'rows': 3}),
            'Cantidad': forms.NumberInput(attrs={'placeholder': 'Editar cantidad'}),
            'CantidadMinimaSugerida': forms.NumberInput(attrs={'placeholder': 'Editar cantidad mínima sugerida'}),
            'UnidadDeMedida': forms.Select(attrs={'placeholder': 'Editar unidad de medida'}),
            'PrecioCosto': forms.NumberInput(attrs={'placeholder': 'Editar precio de costo'}),
            'PrecioDeLista': forms.NumberInput(attrs={'placeholder': 'Editar precio de lista'}),
            'PrecioDeContado': forms.NumberInput(attrs={'placeholder': 'Editar precio de contado'}),
        }

class AddCategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['Nombre']
        labels = {
            'Nombre': 'Nombre',
        }

class EditCategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['Nombre']
        labels = {
            'Nombre': 'Nombre:',
        }
        widgets = {
            'Nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '', 'id': 'nombre_editar'}),
        }

class VentaForm(forms.ModelForm):
    class Meta:
        model = Venta
        fields = ['Cliente', 'ImporteTotal', 'Caja', 'Cajero']
        # Asegúrate de que MedioDePago no esté aquí

class LoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Usuario'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Contraseña'})
    )

class RegisterForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Correo electrónico'
        }),
        label=""
    )
    first_name = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nombre'
        }),
        label=""
    )
    last_name = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Apellido'
        }),
        label=""
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)
        # Personalizar los widgets y quitar las etiquetas
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Nombre de usuario'
        })
        self.fields['username'].label = ""

        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Contraseña'
        })
        self.fields['password1'].label = ""
        self.fields['password1'].help_text = "La contraseña debe tener al menos 8 caracteres y no puede ser común"

        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirmar contraseña'
        })
        self.fields['password2'].label = ""
        self.fields['password2'].help_text = "Ingresa la misma contraseña para verificar"

class PagoVentaForm(forms.ModelForm):
    class Meta:
        model = PagoVenta
        fields = ['MedioDePago', 'Monto', 'DatosAdicionales']

# Formulario para MovimientoStock (para ajustes manuales)
class MovimientoStockForm(forms.ModelForm):
    class Meta:
        model = MovimientoStock
        fields = ['Producto', 'Tipo', 'Cantidad', 'OrigenMovimiento', 'Observaciones']
        widgets = {
            'Producto': forms.Select(attrs={'class': 'form-control select2'}),
            'Tipo': forms.Select(attrs={'class': 'form-control'}),
            'Cantidad': forms.NumberInput(attrs={'class': 'form-control', 'min': '0.01', 'step': '0.01'}),
            'OrigenMovimiento': forms.Select(attrs={'class': 'form-control'}),
            'Observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


# Formulario para búsqueda de movimientos de stock
class BusquedaMovimientosForm(forms.Form):
    producto = forms.ModelChoiceField(
        queryset=Producto.objects.all().order_by('Nombre'),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control select2'})
    )
    tipo = forms.ChoiceField(
        choices=[('', 'Todos')] + list(MovimientoStock.TIPO_CHOICES),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    origen = forms.ChoiceField(
        choices=[('', 'Todos')] + list(MovimientoStock.ORIGEN_CHOICES),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    fecha_desde = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    fecha_hasta = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )

# Formulario de PagoCompra
class PagoCompraForm(forms.ModelForm):
    class Meta:
        model = PagoCompra
        fields = ['Compra', 'MedioDePago', 'Monto']
        widgets = {
            'Compra': forms.HiddenInput(),  # Este campo se llenará automáticamente
            'Monto': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'MedioDePago': forms.Select(attrs={
                'class': 'form-control'
            })
        }