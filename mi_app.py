import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
from tkinter import scrolledtext
from datetime import datetime, timedelta
import os
import webbrowser
import json
import tempfile
import qrcode
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pyttsx3
import threading
import speech_recognition as sr
import webbrowser
import random



# ================= CONFIGURACIÓN INICIAL =================
# Diccionario para almacenar los productos y ventas
inventario = {}
ventas = []
clientes = {}
proveedores = {}
usuarios = {}
categorias = ["Electrónica", "Alimentos", "Ropa", "Hogar", "Oficina", "General"]

# Configuración de colores mejorada
COLOR_PRIMARIO = "#2c3e50"
COLOR_SECUNDARIO = "#34495e"
COLOR_TERCIARIO = "#3498db"
COLOR_FONDO = "#c1e207"
COLOR_TEXTO = "#2c3e50"
COLOR_TEXTO_CLARO = "#ecf0f1"
COLOR_EXITO = "#2ecc71"
COLOR_ALERTA = "#e74c3c"
COLOR_ADVERTENCIA = "#f39c12"

# Variables globales
carrito = {}
total_venta = 0.0
usuario_actual = None
modo_oscuro = False
asistente_activo = True
hilo_wilson = None
ultimo_ticket = ""

# ================= CLASES =================
class Producto:
    def __init__(self, nombre, cantidad, precio, categoria="General", proveedor="", minimo=5, fecha_actualizacion=None, costo=0):
        self.nombre = nombre
        self.cantidad = cantidad
        self.precio = precio
        self.categoria = categoria
        self.proveedor = proveedor
        self.minimo = minimo
        self.fecha_actualizacion = fecha_actualizacion or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.costo = costo  # NUEVO

# ...existing code...
sucursales = {}

class Sucursal:
    def __init__(self, nombre, direccion, empleado_asignado=""):
        self.nombre = nombre
        self.direccion = direccion
        self.empleado_asignado = empleado_asignado
class Venta:
    def __init__(self, productos, total, cliente="Consumidor Final", metodo_pago="Efectivo", monto_recibido=0):
        self.productos = productos
        self.total = total
        self.fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.cliente = cliente
        self.metodo_pago = metodo_pago
        self.vendedor = usuario_actual.username if usuario_actual else "Anónimo"
        self.monto_recibido = monto_recibido
        self.cambio = monto_recibido - total if metodo_pago == "Efectivo" else 0

class Cliente:
    def __init__(self, nombre, nit, direccion="", telefono="", email=""):
        self.nombre = nombre
        self.nit = nit
        self.direccion = direccion
        self.telefono = telefono
        self.email = email
        self.historial_compras = []

class Proveedor:
    def __init__(self, nombre, contacto, telefono, productos=[], plazo_entrega="7 días"):
        self.nombre = nombre
        self.contacto = contacto
        self.telefono = telefono
        self.productos = productos
        self.plazo_entrega = plazo_entrega

class Usuario:
    def __init__(self, username, password, rol="empleado", proveedor_asociado="", sucursal_asignada=""):
        self.username = username
        self.password = password
        self.rol = rol  # 'admin', 'proveedor', 'empleado'
        self.proveedor_asociado = proveedor_asociado
        self.sucursal_asignada = sucursal_asignada  # NUEVO

# ================= FUNCIONES DE DATOS =================
def guardar_datos():
    datos = {
        'inventario': {nombre: {
            'nombre': producto.nombre,
            'cantidad': producto.cantidad,
            'precio': producto.precio,
            'costo': producto.costo,  # NUEVO
            'categoria': producto.categoria,
            'proveedor': producto.proveedor,
            'minimo': producto.minimo,
            'fecha_actualizacion': producto.fecha_actualizacion
        } for nombre, producto in inventario.items()},
        'ventas': [{
            'productos': venta.productos,
            'total': venta.total,
            'fecha': venta.fecha,
            'cliente': venta.cliente,
            'metodo_pago': venta.metodo_pago,
            'vendedor': venta.vendedor,
            'monto_recibido': venta.monto_recibido,
            'cambio': venta.cambio
        } for venta in ventas],
        'clientes': {nit: {
            'nombre': cliente.nombre,
            'nit': cliente.nit,
            'direccion': cliente.direccion,
            'telefono': cliente.telefono,
            'email': cliente.email,
            'historial_compras': cliente.historial_compras
        } for nit, cliente in clientes.items()},
        'proveedores': {nombre: {
            'nombre': proveedor.nombre,
            'contacto': proveedor.contacto,
            'telefono': proveedor.telefono,
            'productos': proveedor.productos,
            'plazo_entrega': proveedor.plazo_entrega
        } for nombre, proveedor in proveedores.items()},
        'usuarios': {username: {
            'username': usuario.username,
            'password': usuario.password,
            'rol': usuario.rol,
            'proveedor_asociado': usuario.proveedor_asociado
        } for username, usuario in usuarios.items()},
        'categorias': categorias
    }
    with open('datos_sistema.json', 'w') as f:
        json.dump(datos, f, indent=4)

def cargar_datos():
    global categorias
    try:
        with open('datos_sistema.json', 'r') as f:
            datos = json.load(f)
            
            inventario.clear()
            for nombre, attrs in datos['inventario'].items():
                inventario[nombre] = Producto(
                    nombre=attrs['nombre'],
                    cantidad=attrs['cantidad'],
                    precio=attrs['precio'],
                    categoria=attrs['categoria'],
                    proveedor=attrs['proveedor'],
                    minimo=attrs['minimo'],
                    fecha_actualizacion=attrs.get('fecha_actualizacion'),
                    costo=attrs.get('costo', 0)  # NUEVO
                )
                
            ventas.clear()
            for venta_data in datos['ventas']:
                ventas.append(Venta(
                    productos=venta_data['productos'],
                    total=venta_data['total'],
                    cliente=venta_data['cliente'],
                    metodo_pago=venta_data['metodo_pago'],
                    monto_recibido=venta_data.get('monto_recibido', 0)
                ))
                
            clientes.clear()
            for nit, attrs in datos['clientes'].items():
                cliente = Cliente(
                    nombre=attrs['nombre'],
                    nit=attrs['nit'],
                    direccion=attrs['direccion'],
                    telefono=attrs['telefono'],
                    email=attrs['email']
                )
                cliente.historial_compras = attrs['historial_compras']
                clientes[nit] = cliente
                
            proveedores.clear()
            for nombre, attrs in datos['proveedores'].items():
                proveedores[nombre] = Proveedor(
                    nombre=attrs['nombre'],
                    contacto=attrs['contacto'],
                    telefono=attrs['telefono'],
                    productos=attrs['productos'],
                    plazo_entrega=attrs['plazo_entrega']
                )
                
            usuarios.clear()
            for username, attrs in datos['usuarios'].items():
                usuarios[username] = Usuario(
                    username=attrs['username'],
                    password=attrs['password'],
                    rol=attrs['rol'],
                    proveedor_asociado=attrs['proveedor_asociado']
                )
                
            categorias = datos.get('categorias', categorias)
            
    except FileNotFoundError:
        cargar_datos_ejemplo()

# ================= INTERFAZ DE USUARIO =================
def mostrar_login():
    login_window = tk.Toplevel(ventana)
    login_window.title("Inicio de Sesión")
    login_window.geometry("1000x900")
    login_window.resizable(False, False)
    login_window.grab_set()
    
    # Estilo
    login_window.configure(bg=COLOR_PRIMARIO)
    
    # Marco principal
    frame_login = ttk.Frame(login_window, padding=20, style='Login.TFrame')
    frame_login.pack(fill=tk.BOTH, expand=True)
    
    # Logo (puedes reemplazar con tu propio logo)
    logo_label = ttk.Label(frame_login, text="⚙️", font=("Arial", 48), style='Login.TLabel')
    logo_label.pack(pady=10)
    
    ttk.Label(frame_login, text="Sistema de Gestión", font=("Arial", 16, "bold"), style='Login.TLabel').pack(pady=5)
    
    # Campos de entrada
    frame_campos = ttk.Frame(frame_login, style='Login.TFrame')
    frame_campos.pack(pady=20)
    
    ttk.Label(frame_campos, text="Usuario:", style='Login.TLabel').grid(row=0, column=0, pady=5, sticky=tk.W)
    entry_usuario = ttk.Entry(frame_campos, font=("Arial", 12))
    entry_usuario.grid(row=0, column=1, pady=5, padx=5)
    
    ttk.Label(frame_campos, text="Contraseña:", style='Login.TLabel').grid(row=1, column=0, pady=5, sticky=tk.W)
    entry_password = ttk.Entry(frame_campos, show="*", font=("Arial", 12))
    entry_password.grid(row=1, column=1, pady=5, padx=5)
    
    # Botón de ingreso
    def verificar_login():
        global usuario_actual
        username = entry_usuario.get()
        password = entry_password.get()
        
        if username in usuarios and usuarios[username].password == password:
            usuario_actual = usuarios[username]
            login_window.destroy()
            actualizar_interfaz_segun_rol()
            ventana.deiconify()
            messagebox.showinfo("Bienvenido", f"¡Hola {usuario_actual.username}! Bienvenido al sistema.")

            # Mostrar dashboard si es admin
            if usuario_actual.rol == 'admin':
                mostrar_dashboard()
        else:
            messagebox.showerror("Error", "Usuario o contraseña incorrectos", parent=login_window)
    
    btn_ingresar = ttk.Button(frame_login, text="Ingresar", command=verificar_login, style='Login.TButton')
    btn_ingresar.pack(pady=20)
    
    # Estilos específicos para login
    estilo.configure('Login.TFrame', background=COLOR_PRIMARIO)
    estilo.configure('Login.TLabel', background=COLOR_PRIMARIO, foreground=COLOR_TEXTO_CLARO, font=("Arial", 12))
    estilo.configure('Login.TButton', background=COLOR_TERCIARIO, foreground=COLOR_TEXTO_CLARO, 
                    font=("Arial", 12, "bold"), padding=10)
    
    entry_usuario.focus_set()
    ventana.withdraw()

def actualizar_interfaz_segun_rol():
    # Actualizar pestañas según rol
    if usuario_actual.rol == 'admin':
        notebook.tab(0, state='normal')  # Inventario
        notebook.tab(1, state='normal')  # Ventas
        notebook.tab(2, state='normal')  # Reportes
        notebook.tab(3, state='normal')  # Dashboard
        menu_gestion.entryconfig("Clientes", state='normal')
        menu_gestion.entryconfig("Proveedores", state='normal')
        menu_gestion.entryconfig("Categorías", state='normal')
        menu_gestion.entryconfig("Usuarios", state='normal')
        menu_gestion.entryconfig("Historial de Ventas", state='normal')
    elif usuario_actual.rol == 'proveedor':
        notebook.tab(0, state='normal')  # Inventario
        notebook.tab(1, state='normal')  # Ventas
        notebook.tab(2, state='disabled')  # Reportes
        notebook.tab(3, state='disabled')  # Dashboard
        menu_gestion.entryconfig("Clientes", state='disabled')
        menu_gestion.entryconfig("Proveedores", state='disabled')
        menu_gestion.entryconfig("Categorías", state='disabled')
        menu_gestion.entryconfig("Usuarios", state='disabled')
        menu_gestion.entryconfig("Historial de Ventas", state='disabled')
    elif usuario_actual.rol == 'empleado':
        notebook.tab(0, state='disabled')  # Inventario
        notebook.tab(1, state='normal')  # Ventas
        notebook.tab(2, state='disabled')  # Reportes
        notebook.tab(3, state='disabled')  # Dashboard
        menu_gestion.entryconfig("Clientes", state='normal')
        menu_gestion.entryconfig("Proveedores", state='disabled')
        menu_gestion.entryconfig("Categorías", state='disabled')
        menu_gestion.entryconfig("Usuarios", state='disabled')
        menu_gestion.entryconfig("Historial de Ventas", state='disabled')
    
    # Actualizar lista de productos según proveedor (si aplica)
    if usuario_actual.rol == 'proveedor':
        sincronizar_inventario_ventas(usuario_actual.proveedor_asociado)
    else:
        sincronizar_inventario_ventas()

# ================= FUNCIONES DE INVENTARIO =================
def agregar_producto():
    nombre = entry_nombre.get().strip()
    try:
        cantidad = int(entry_cantidad.get())
        precio = float(entry_precio.get())
        costo = float(entry_costo.get()) if entry_costo.get() else 0  # NUEVO
        minimo = int(entry_minimo.get()) if entry_minimo.get() else 5
    except ValueError:
        messagebox.showerror("Error", "Por favor ingrese valores numéricos válidos.")
        return

    if not nombre:
        messagebox.showwarning("Advertencia", "El nombre del producto no puede estar vacío.")
        return

    ganancia = precio - costo  # NUEVO
    messagebox.showinfo("Ganancia", f"La ganancia por unidad será: Bs {ganancia:.2f}")

    categoria = combo_categoria.get()
    proveedor = combo_proveedor.get()

    # Si es proveedor, solo puede agregar productos de su proveedor
    if usuario_actual and usuario_actual.rol == 'proveedor':
        proveedor = usuario_actual.proveedor_asociado

    if nombre in inventario:
        respuesta = messagebox.askyesno("Confirmación", 
                        "El producto ya existe. ¿Desea actualizar sus datos?")
        if respuesta:
            inventario[nombre] = Producto(nombre, cantidad, precio, categoria, proveedor, minimo, costo=costo)
            actualizar_lista()
            limpiar_campos()
    else:
        inventario[nombre] = Producto(nombre, cantidad, precio, categoria, proveedor, minimo, costo=costo)
        actualizar_lista()
        limpiar_campos()
        messagebox.showinfo("Éxito", f"Producto '{nombre}' agregado correctamente.")


def eliminar_producto():
    seleccionado = lista_inventario.selection()
    if seleccionado:
        nombre = lista_inventario.item(seleccionado, 'values')[0]
        
        # Verificar si el usuario tiene permisos para eliminar este producto
        if usuario_actual.rol == 'proveedor' and inventario[nombre].proveedor != usuario_actual.proveedor_asociado:
            messagebox.showerror("Error", "Solo puede eliminar productos de su proveedor.")
            return
            
        respuesta = messagebox.askyesno("Confirmar eliminación", 
                      f"¿Está seguro de eliminar el producto '{nombre}'?")
        if respuesta:
            del inventario[nombre]
            actualizar_lista()
    else:
        messagebox.showinfo("Información", "Por favor seleccione un producto de la lista.")

def modificar_producto():
    seleccionado = lista_inventario.selection()
    if seleccionado:
        nombre = lista_inventario.item(seleccionado, 'values')[0]
        producto = inventario[nombre]
        
        # Verificar permisos para proveedores
        if usuario_actual and usuario_actual.rol == 'proveedor' and producto.proveedor != usuario_actual.proveedor_asociado:
            messagebox.showerror("Error", "Solo puede modificar productos de su proveedor.")
            return
        
        # Crear ventana de edición
        ventana_edicion = tk.Toplevel(ventana)
        ventana_edicion.title(f"Editar {nombre}")
        ventana_edicion.geometry("400x400")
        ventana_edicion.resizable(False, False)
        
        # Estilo
        ventana_edicion.configure(bg=COLOR_FONDO)
        
        # Campos de edición
        ttk.Label(ventana_edicion, text="Nombre:").pack()
        entry_nombre_edit = ttk.Entry(ventana_edicion, font=("Arial", 12))
        entry_nombre_edit.insert(0, producto.nombre)
        entry_nombre_edit.pack(pady=5)
        
        ttk.Label(ventana_edicion, text="Cantidad:").pack()
        entry_cantidad_edit = ttk.Entry(ventana_edicion, font=("Arial", 12))
        entry_cantidad_edit.insert(0, str(producto.cantidad))
        entry_cantidad_edit.pack(pady=5)
        
        ttk.Label(ventana_edicion, text="Precio:").pack()
        entry_precio_edit = ttk.Entry(ventana_edicion, font=("Arial", 12))
        entry_precio_edit.insert(0, str(producto.precio))
        entry_precio_edit.pack(pady=5)
        
        ttk.Label(ventana_edicion, text="Categoría:").pack()
        combo_categoria_edit = ttk.Combobox(ventana_edicion, values=categorias, font=("Arial", 12))
        combo_categoria_edit.set(producto.categoria)
        combo_categoria_edit.pack(pady=5)
        
        ttk.Label(ventana_edicion, text="Proveedor:").pack()
        combo_proveedor_edit = ttk.Combobox(ventana_edicion, values=list(proveedores.keys()), font=("Arial", 12))
        combo_proveedor_edit.set(producto.proveedor)
        combo_proveedor_edit.pack(pady=5)
        
        # Si es proveedor, no puede cambiar el proveedor
        if usuario_actual and usuario_actual.rol == 'proveedor':
            combo_proveedor_edit.config(state='disabled')
        
        ttk.Label(ventana_edicion, text="Stock mínimo:").pack()
        entry_minimo_edit = ttk.Entry(ventana_edicion, font=("Arial", 12))
        entry_minimo_edit.insert(0, str(producto.minimo))
        entry_minimo_edit.pack(pady=5)
        
        def guardar_cambios():
            try:
                nuevo_nombre = entry_nombre_edit.get().strip()
                nueva_cantidad = int(entry_cantidad_edit.get())
                nuevo_precio = float(entry_precio_edit.get())
                nueva_categoria = combo_categoria_edit.get()
                nuevo_proveedor = combo_proveedor_edit.get()
                nuevo_minimo = int(entry_minimo_edit.get())
                
                if not nuevo_nombre:
                    messagebox.showwarning("Advertencia", "El nombre no puede estar vacío.")
                    return
                
                # Si cambió el nombre, eliminar el viejo y crear uno nuevo
                if nuevo_nombre != nombre:
                    del inventario[nombre]
                    inventario[nuevo_nombre] = Producto(nuevo_nombre, nueva_cantidad, nuevo_precio, 
                                                      nueva_categoria, nuevo_proveedor, nuevo_minimo)
                else:
                    # Actualizar el producto existente
                    producto.cantidad = nueva_cantidad
                    producto.precio = nuevo_precio
                    producto.categoria = nueva_categoria
                    producto.proveedor = nuevo_proveedor
                    producto.minimo = nuevo_minimo
                    producto.fecha_actualizacion = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                actualizar_lista()
                ventana_edicion.destroy()
                messagebox.showinfo("Éxito", "Producto actualizado correctamente.")
            except ValueError:
                messagebox.showerror("Error", "Por favor ingrese valores válidos.")
        
        btn_guardar = ttk.Button(ventana_edicion, text="Guardar Cambios", command=guardar_cambios, style='Accion.TButton')
        btn_guardar.pack(pady=10)
    else:
        messagebox.showinfo("Información", "Por favor seleccione un producto de la lista.")

def buscar_producto():
    nombre = entry_nombre.get().strip()
    if nombre in inventario:
        producto = inventario[nombre]
        messagebox.showinfo("Producto encontrado", 
            f"Nombre: {producto.nombre}\n"
            f"Cantidad: {producto.cantidad} unidades\n"
            f"Precio unitario: Bs {producto.precio:.2f}\n"
            f"Categoría: {producto.categoria}\n"
            f"Proveedor: {producto.proveedor}\n"
            f"Stock mínimo: {producto.minimo}\n"
            f"Última actualización: {producto.fecha_actualizacion}")
    else:
        messagebox.showerror("No encontrado", 
            f"El producto '{nombre}' no existe en el inventario.")

def actualizar_lista():
    # Limpiar la lista
    for item in lista_inventario.get_children():
        lista_inventario.delete(item)
    
    # Filtrar productos si es proveedor
    productos_mostrar = inventario.values()
    if usuario_actual and usuario_actual.rol == 'proveedor':
        productos_mostrar = [p for p in inventario.values() if p.proveedor == usuario_actual.proveedor_asociado]
    
    # Agregar productos ordenados alfabéticamente
    for producto in sorted(productos_mostrar, key=lambda x: x.nombre):
        lista_inventario.insert("", "end", values=(
            producto.nombre, 
            producto.cantidad,
            f"Bs {producto.precio:.2f}",
            producto.categoria,
            producto.proveedor,
            producto.minimo,
            "⚠️" if producto.cantidad < producto.minimo else ""
        ))
    
    # Resaltar productos con stock bajo
    lista_inventario.tag_configure('bajo', background='#ffdddd')
    for item in lista_inventario.get_children():
        valores = lista_inventario.item(item, 'values')
        if valores and inventario[valores[0]].cantidad < inventario[valores[0]].minimo:
            lista_inventario.item(item, tags=('bajo',))

def limpiar_campos():
    entry_nombre.delete(0, tk.END)
    entry_cantidad.delete(0, tk.END)
    entry_precio.delete(0, tk.END)
    entry_minimo.delete(0, tk.END)
    combo_categoria.set("General")
    combo_proveedor.set("")
    entry_nombre.focus_set()

# ================= FUNCIONES DE VENTAS =================
def agregar_al_carrito():
    seleccionado = lista_inventario_ventas.selection()
    if not seleccionado:
        messagebox.showwarning("Advertencia", "Seleccione un producto del inventario.")
        return
    
    nombre = lista_inventario_ventas.item(seleccionado, 'values')[0]
    producto = inventario[nombre]
    
    # Pedir cantidad a vender
    cantidad = simpledialog.askinteger("Cantidad a vender", 
                     f"Ingrese la cantidad a vender de '{nombre}' (Disponible: {producto.cantidad}):",
                     minvalue=1, maxvalue=producto.cantidad, parent=ventana)
    
    if cantidad is None:  # El usuario canceló
        return
    
    if nombre in carrito:
        carrito[nombre]["cantidad"] += cantidad
    else:
        carrito[nombre] = {
            "cantidad": cantidad,
            "precio": producto.precio,
            "categoria": producto.categoria
        }
    
    # Actualizar inventario temporalmente (se confirmará al finalizar la venta)
    inventario[nombre].cantidad -= cantidad
    
    actualizar_carrito()
    sincronizar_inventario_ventas()

def actualizar_carrito():
    global total_venta
    total_venta = 0.0
    
    # Limpiar el carrito
    for item in lista_carrito.get_children():
        lista_carrito.delete(item)
    
    # Agregar productos al carrito
    for producto, datos in carrito.items():
        subtotal = datos["cantidad"] * datos["precio"]
        total_venta += subtotal
        lista_carrito.insert("", "end", values=(
            producto,
            datos["cantidad"],
            f"Bs {datos['precio']:.2f}",
            f"Bs {subtotal:.2f}"
        ))
    
    # Actualizar total
    label_total.config(text=f"Total a Pagar: Bs {total_venta:.2f}")

def eliminar_del_carrito():
    seleccionado = lista_carrito.selection()
    if not seleccionado:
        messagebox.showwarning("Advertencia", "Seleccione un producto del carrito.")
        return
    
    nombre = lista_carrito.item(seleccionado, 'values')[0]
    
    # Devolver la cantidad al inventario
    cantidad_devuelta = carrito[nombre]["cantidad"]
    inventario[nombre].cantidad += cantidad_devuelta
    
    # Eliminar del carrito
    del carrito[nombre]
    
    actualizar_carrito()
    sincronizar_inventario_ventas()

def finalizar_venta():
    global total_venta, carrito
    
    if not carrito:
        messagebox.showwarning("Advertencia", "El carrito está vacío.")
        return
    
    # Crear ventana de confirmación
    ventana_confirmacion = tk.Toplevel(ventana)
    ventana_confirmacion.title("Confirmar Venta")
    ventana_confirmacion.geometry("500x600")
    ventana_confirmacion.resizable(False, False)
    
    # Estilo
    ventana_confirmacion.configure(bg=COLOR_FONDO)
    
    # Información del cliente
    ttk.Label(ventana_confirmacion, text="Datos del Cliente", font=("Arial", 14, "bold")).pack(pady=10)
    
    frame_cliente = ttk.Frame(ventana_confirmacion)
    frame_cliente.pack(pady=5)
    
    ttk.Label(frame_cliente, text="Nombre:").grid(row=0, column=0, sticky=tk.W, pady=5)
    entry_cliente = ttk.Entry(frame_cliente, font=("Arial", 12))
    entry_cliente.grid(row=0, column=1, pady=5, padx=5)
    
    ttk.Label(frame_cliente, text="NIT/CI:").grid(row=1, column=0, sticky=tk.W, pady=5)
    entry_nit = ttk.Entry(frame_cliente, font=("Arial", 12))
    entry_nit.grid(row=1, column=1, pady=5, padx=5)
    
    # Método de pago
    ttk.Label(ventana_confirmacion, text="Método de Pago", font=("Arial", 14, "bold")).pack(pady=10)
    
    metodo_pago = tk.StringVar(value="Efectivo")
    frame_metodo = ttk.Frame(ventana_confirmacion)
    frame_metodo.pack(pady=5)
    
    ttk.Radiobutton(frame_metodo, text="Efectivo", variable=metodo_pago, value="Efectivo").grid(row=0, column=0, sticky=tk.W)
    ttk.Radiobutton(frame_metodo, text="Tarjeta", variable=metodo_pago, value="Tarjeta").grid(row=1, column=0, sticky=tk.W)
    ttk.Radiobutton(frame_metodo, text="Transferencia", variable=metodo_pago, value="Transferencia").grid(row=2, column=0, sticky=tk.W)
    ttk.Radiobutton(frame_metodo, text="QR", variable=metodo_pago, value="QR").grid(row=3, column=0, sticky=tk.W)
    
    # Campo para monto recibido (solo efectivo)
    frame_monto = ttk.Frame(ventana_confirmacion)
    frame_monto.pack(pady=5)
    
    ttk.Label(frame_monto, text="Monto recibido (Bs):").grid(row=0, column=0, sticky=tk.W)
    entry_monto = ttk.Entry(frame_monto, font=("Arial", 12))
    entry_monto.grid(row=0, column=1, padx=5)
    
    def actualizar_cambio():
        if metodo_pago.get() == "Efectivo":
            try:
                monto = float(entry_monto.get())
                cambio = monto - total_venta
                if cambio >= 0:
                    label_cambio.config(text=f"Cambio: Bs {cambio:.2f}", foreground="green")
                else:
                    label_cambio.config(text=f"Faltan: Bs {-cambio:.2f}", foreground="red")
            except ValueError:
                label_cambio.config(text="Ingrese un monto válido", foreground="red")
    
    # Bind para actualizar cambio automáticamente
    entry_monto.bind("<KeyRelease>", lambda e: actualizar_cambio())
    
    label_cambio = ttk.Label(ventana_confirmacion, text="", font=("Arial", 12, "bold"))
    label_cambio.pack(pady=5)
    
    # Resumen de venta
    ttk.Label(ventana_confirmacion, text="Resumen de Venta", font=("Arial", 14, "bold")).pack(pady=10)
    
    frame_resumen = ttk.Frame(ventana_confirmacion)
    frame_resumen.pack(pady=5)
    
    ttk.Label(frame_resumen, text="Producto").grid(row=0, column=0, sticky=tk.W)
    ttk.Label(frame_resumen, text="Cant").grid(row=0, column=1)
    ttk.Label(frame_resumen, text="P.Unit").grid(row=0, column=2)
    ttk.Label(frame_resumen, text="Subtotal").grid(row=0, column=3)
    
    row = 1
    for producto, datos in carrito.items():
        subtotal = datos["cantidad"] * datos["precio"]
        ttk.Label(frame_resumen, text=producto[:15]).grid(row=row, column=0, sticky=tk.W)
        ttk.Label(frame_resumen, text=str(datos["cantidad"])).grid(row=row, column=1)
        ttk.Label(frame_resumen, text=f"{datos['precio']:.2f}").grid(row=row, column=2)
        ttk.Label(frame_resumen, text=f"{subtotal:.2f}").grid(row=row, column=3)
        row += 1
    
    ttk.Label(ventana_confirmacion, text=f"Total: Bs {total_venta:.2f}", font=("Arial", 12, "bold")).pack(pady=10)
    
    def confirmar_y_guardar():
        cliente_nombre = entry_cliente.get().strip() or "Consumidor Final"
        cliente_nit = entry_nit.get().strip() or "0"
        metodo = metodo_pago.get()
        
        # Validar monto si es pago en efectivo
        if metodo == "Efectivo":
            try:
                monto_recibido = float(entry_monto.get())
                if monto_recibido < total_venta:
                    messagebox.showerror("Error", "El monto recibido es menor al total a pagar.")
                    return
            except ValueError:
                messagebox.showerror("Error", "Ingrese un monto válido para pago en efectivo.")
                return
        else:
            monto_recibido = 0
        
        # Si es pago con QR, mostrar código QR
        if metodo == "QR":
            mostrar_qr_pago(total_venta)
        
        # Registrar la venta
        nueva_venta = Venta(carrito.copy(), total_venta, cliente_nombre, metodo, monto_recibido)
        ventas.append(nueva_venta)
        
        # Registrar cliente si no existe
        if cliente_nit != "0" and cliente_nit not in clientes:
            clientes[cliente_nit] = Cliente(cliente_nombre, cliente_nit)
        
        # Actualizar historial del cliente
        if cliente_nit != "0":
            clientes[cliente_nit].historial_compras.append({
                "fecha": nueva_venta.fecha,
                "total": nueva_venta.total,
                "productos": list(nueva_venta.productos.keys())
            })
        
        # Generar ticket
        generar_ticket(nueva_venta)
        global ultimo_ticket
        ultimo_ticket = generar_ticket(nueva_venta)
        
        # Limpiar carrito
        carrito.clear()
        actualizar_carrito()
        sincronizar_inventario_ventas()
        
        ventana_confirmacion.destroy()
        messagebox.showinfo("Venta completada", "La venta se ha registrado correctamente.")
    
    btn_confirmar = ttk.Button(ventana_confirmacion, text="Confirmar Venta", 
                              command=confirmar_y_guardar, style='Accion.TButton')
    btn_confirmar.pack(pady=10)

def mostrar_qr_pago(monto):
    qr_window = tk.Toplevel(ventana)
    qr_window.title("Pago con QR")
    qr_window.geometry("350x450")
    qr_window.resizable(False, False)
    qr_window.attributes('-topmost', True)

    try:
        # Cargar tu imagen de QR personalizada desde la ruta absoluta
        ruta_qr = r"C:\Users\HP\Desktop\licoreria en html\ideas\qr\qrdepago.png"
        img_qr = Image.open(ruta_qr)
        img_qr.thumbnail((300, 300))
        img_qr_tk = ImageTk.PhotoImage(img_qr)

        # Mostrar el QR
        ttk.Label(qr_window, text="Escanea el código para pagar", font=("Arial", 12, "bold")).pack(pady=10)
        label_qr = ttk.Label(qr_window, image=img_qr_tk)
        label_qr.image = img_qr_tk
        label_qr.pack(pady=10)

        ttk.Label(qr_window, text=f"Monto a pagar: Bs {monto:.2f}", font=("Arial", 12)).pack(pady=5)
        ttk.Label(qr_window, text=f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M')}").pack(pady=5)

        ttk.Button(qr_window, text="Cerrar", command=qr_window.destroy, style='Accion.TButton').pack(pady=10)
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo mostrar el código QR:\n{str(e)}")
        qr_window.destroy()
        
def cancelar_venta():
    global carrito
    
    if not carrito:
        return
    
    respuesta = messagebox.askyesno("Cancelar venta", 
                  "¿Está seguro de cancelar la venta? Se devolverán los productos al inventario.")
    
    if respuesta:
        # Devolver todos los productos al inventario
        for producto, datos in carrito.items():
            inventario[producto].cantidad += datos["cantidad"]
        
        carrito.clear()
        actualizar_carrito()
        sincronizar_inventario_ventas()
        texto_ticket.config(state=tk.NORMAL)
        texto_ticket.delete(1.0, tk.END)
        texto_ticket.config(state=tk.DISABLED)

def generar_ticket(venta):
    ticket = "=== EL CHAUEÑASO ===\n"
    ticket += f"Fecha: {venta.fecha}\n"
    ticket += f"Cliente: {venta.cliente}\n"
    ticket += f"Vendedor: {venta.vendedor}\n"
    ticket += f"Método de pago: {venta.metodo_pago}\n"
    
    if venta.metodo_pago == "Efectivo":
        ticket += f"Monto recibido: Bs {venta.monto_recibido:.2f}\n"
        ticket += f"Cambio: Bs {venta.cambio:.2f}\n"
    
    ticket += "-"*50 + "\n"
    ticket += "Producto           Cant   P.Unit   Subtotal\n"
    ticket += "-"*50 + "\n"
    
    for producto, datos in venta.productos.items():
        subtotal = datos["cantidad"] * datos["precio"]
        ticket += f"{producto[:18]:<18} {datos['cantidad']:>4}  {datos['precio']:>7.2f}  {subtotal:>9.2f}\n"
    
    ticket += "-"*50 + "\n"
    ticket += f"TOTAL: Bs {venta.total:.2f}\n"
    ticket += "-"*50 + "\n"
    ticket += "¡Gracias por su compra!\n"
    
    # Mostrar ticket en el área de texto
    texto_ticket.config(state=tk.NORMAL)
    texto_ticket.delete(1.0, tk.END)
    texto_ticket.insert(tk.END, ticket)
    texto_ticket.config(state=tk.DISABLED)
    
    return ticket

def imprimir_ticket():
    global ultimo_ticket
    if not ultimo_ticket.strip():
        messagebox.showwarning("Advertencia", "No hay ticket para imprimir.")
        return

    # Crear un archivo PDF temporal
    temp_pdf = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
    pdf_path = temp_pdf.name
    temp_pdf.close()

    try:
        c = canvas.Canvas(pdf_path, pagesize=(200, 300))
        width, height = 200, 300

        # Imprime el texto del último ticket línea por línea
        y_position = height - 20
        c.setFont("Helvetica", 8)
        for linea in ultimo_ticket.splitlines():
            c.drawString(10, y_position, linea)
            y_position -= 12
            if y_position < 20:
                c.showPage()
                y_position = height - 20

        c.save()
        webbrowser.open(pdf_path)
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo generar el PDF:\n{str(e)}")
        if os.path.exists(pdf_path):
            os.remove(pdf_path)
        
        # Totales
        c.line(10, y_position-5, 190, y_position-5)
        y_position -= 15
        
        c.drawString(20, y_position, "TOTAL:")
        c.drawString(160, y_position, f"Bs {total_venta:.2f}")
        y_position -= 15
        
        # Método de pago
        c.drawString(20, y_position, "Método de pago:")
        c.drawString(160, y_position, "Efectivo")  # Aquí deberías usar el método real
        
        c.save()
        webbrowser.open(pdf_path)
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo generar el PDF:\n{str(e)}")
        if os.path.exists(pdf_path):
            os.remove(pdf_path)

def guardar_ticket():
    if not texto_ticket.get(1.0, tk.END).strip():
        messagebox.showwarning("Advertencia", "No hay ticket para guardar.")
        return
    
    archivo = filedialog.asksaveasfilename(
        defaultextension=".txt",
        filetypes=[("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")],
        title="Guardar ticket como"
    )
    if archivo:
        try:
            with open(archivo, 'w', encoding='utf-8') as f:
                f.write(texto_ticket.get(1.0, tk.END))
            messagebox.showinfo("Éxito", "Ticket guardado correctamente.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el ticket:\n{str(e)}")

# ================= FUNCIONES DE GESTIÓN =================
def gestionar_clientes():
    ventana_clientes = tk.Toplevel(ventana)
    ventana_clientes.title("Gestión de Clientes")
    ventana_clientes.geometry("900x600")
    
    # Estilo
    ventana_clientes.configure(bg=COLOR_FONDO)
    
    # Marco principal
    frame_principal = ttk.Frame(ventana_clientes)
    frame_principal.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # Lista de clientes
    frame_lista = ttk.Frame(frame_principal)
    frame_lista.pack(fill=tk.BOTH, expand=True)
    
    lista_clientes = ttk.Treeview(frame_lista, columns=("NIT", "Nombre", "Teléfono", "Compras"), show="headings")
    lista_clientes.heading("NIT", text="NIT/CI")
    lista_clientes.heading("Nombre", text="Nombre")
    lista_clientes.heading("Teléfono", text="Teléfono")
    lista_clientes.heading("Compras", text="Compras")
    
    lista_clientes.column("NIT", width=150)
    lista_clientes.column("Nombre", width=250)
    lista_clientes.column("Teléfono", width=150)
    lista_clientes.column("Compras", width=100)
    
    scrollbar = ttk.Scrollbar(frame_lista, orient="vertical", command=lista_clientes.yview)
    lista_clientes.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")
    lista_clientes.pack(fill=tk.BOTH, expand=True)
    
    # Botones
    frame_botones = ttk.Frame(frame_principal)
    frame_botones.pack(fill=tk.X, pady=10)
    
    def actualizar_lista_clientes():
        for item in lista_clientes.get_children():
            lista_clientes.delete(item)
        
        for nit, cliente in clientes.items():
            lista_clientes.insert("", "end", values=(
                nit,
                cliente.nombre,
                cliente.telefono,
                len(cliente.historial_compras)
            ))
    
    def agregar_cliente():
        ventana_agregar = tk.Toplevel(ventana_clientes)
        ventana_agregar.title("Agregar Cliente")
        ventana_agregar.geometry("400x350")
        ventana_agregar.resizable(False, False)
        
        # Campos del formulario
        ttk.Label(ventana_agregar, text="NIT/CI:").pack(pady=5)
        entry_nit = ttk.Entry(ventana_agregar, font=("Arial", 12))
        entry_nit.pack(pady=5)
        
        ttk.Label(ventana_agregar, text="Nombre:").pack(pady=5)
        entry_nombre = ttk.Entry(ventana_agregar, font=("Arial", 12))
        entry_nombre.pack(pady=5)
        
        ttk.Label(ventana_agregar, text="Dirección:").pack(pady=5)
        entry_direccion = ttk.Entry(ventana_agregar, font=("Arial", 12))
        entry_direccion.pack(pady=5)
        
        ttk.Label(ventana_agregar, text="Teléfono:").pack(pady=5)
        entry_telefono = ttk.Entry(ventana_agregar, font=("Arial", 12))
        entry_telefono.pack(pady=5)
        
        ttk.Label(ventana_agregar, text="Email:").pack(pady=5)
        entry_email = ttk.Entry(ventana_agregar, font=("Arial", 12))
        entry_email.pack(pady=5)
        
        def guardar_cliente():
            nit = entry_nit.get().strip()
            nombre = entry_nombre.get().strip()
            
            if not nit or not nombre:
                messagebox.showwarning("Advertencia", "NIT y Nombre son obligatorios.")
                return
            
            clientes[nit] = Cliente(
                nombre,
                nit,
                entry_direccion.get().strip(),
                entry_telefono.get().strip(),
                entry_email.get().strip()
            )
            
            actualizar_lista_clientes()
            ventana_agregar.destroy()
            messagebox.showinfo("Éxito", "Cliente agregado correctamente.")
        
        btn_guardar = ttk.Button(ventana_agregar, text="Guardar", command=guardar_cliente, style='Accion.TButton')
        btn_guardar.pack(pady=10)
    
    def ver_historial():
        seleccionado = lista_clientes.selection()
        if seleccionado:
            nit = lista_clientes.item(seleccionado, 'values')[0]
            cliente = clientes[nit]
            
            ventana_historial = tk.Toplevel(ventana_clientes)
            ventana_historial.title(f"Historial de Compras - {cliente.nombre}")
            ventana_historial.geometry("800x500")
            
            texto = scrolledtext.ScrolledText(ventana_historial, width=100, height=30, font=("Courier", 10))
            texto.pack(fill=tk.BOTH, expand=True)
            
            texto.insert(tk.END, f"Historial de compras de {cliente.nombre} (NIT: {nit})\n")
            texto.insert(tk.END, f"Total compras: {len(cliente.historial_compras)}\n\n")
            
            for compra in cliente.historial_compras:
                texto.insert(tk.END, f"Fecha: {compra['fecha']}\n")
                texto.insert(tk.END, f"Total: Bs {compra['total']:.2f}\n")
                texto.insert(tk.END, f"Productos: {', '.join(compra['productos'][:3])}")
                if len(compra['productos']) > 3:
                    texto.insert(tk.END, f" y {len(compra['productos'])-3} más")
                texto.insert(tk.END, "\n")
                texto.insert(tk.END, "-"*80 + "\n")
            
            texto.config(state=tk.DISABLED)
        else:
            messagebox.showwarning("Advertencia", "Seleccione un cliente para ver su historial.")
    
    btn_agregar = ttk.Button(frame_botones, text="Agregar Cliente", command=agregar_cliente, style='Accion.TButton')
    btn_agregar.pack(side=tk.LEFT, padx=5)
    
    btn_historial = ttk.Button(frame_botones, text="Ver Historial", command=ver_historial)
    btn_historial.pack(side=tk.LEFT, padx=5)
    
    actualizar_lista_clientes()

def gestionar_proveedores():
    ventana_proveedores = tk.Toplevel(ventana)
    ventana_proveedores.title("Gestión de Proveedores")
    ventana_proveedores.geometry("900x600")
    
    # Marco principal
    frame_principal = ttk.Frame(ventana_proveedores)
    frame_principal.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # Lista de proveedores
    frame_lista = ttk.Frame(frame_principal)
    frame_lista.pack(fill=tk.BOTH, expand=True)
    
    lista_proveedores = ttk.Treeview(frame_lista, columns=("Nombre", "Contacto", "Teléfono", "Productos"), show="headings")
    lista_proveedores.heading("Nombre", text="Nombre")
    lista_proveedores.heading("Contacto", text="Contacto")
    lista_proveedores.heading("Teléfono", text="Teléfono")
    lista_proveedores.heading("Productos", text="Productos")
    
    lista_proveedores.column("Nombre", width=200)
    lista_proveedores.column("Contacto", width=150)
    lista_proveedores.column("Teléfono", width=150)
    lista_proveedores.column("Productos", width=300)
    
    scrollbar = ttk.Scrollbar(frame_lista, orient="vertical", command=lista_proveedores.yview)
    lista_proveedores.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")
    lista_proveedores.pack(fill=tk.BOTH, expand=True)
    
    # Botones
    frame_botones = ttk.Frame(frame_principal)
    frame_botones.pack(fill=tk.X, pady=10)
    
    def actualizar_lista_proveedores():
        for item in lista_proveedores.get_children():
            lista_proveedores.delete(item)
        
        for nombre, proveedor in proveedores.items():
            lista_proveedores.insert("", "end", values=(
                nombre,
                proveedor.contacto,
                proveedor.telefono,
                ", ".join(proveedor.productos[:3]) + ("..." if len(proveedor.productos) > 3 else "")
            ))
    
    def agregar_proveedor():
        ventana_agregar = tk.Toplevel(ventana_proveedores)
        ventana_agregar.title("Agregar Proveedor")
        ventana_agregar.geometry("400x300")
        ventana_agregar.resizable(False, False)
        
        ttk.Label(ventana_agregar, text="Nombre:").pack(pady=5)
        entry_nombre = ttk.Entry(ventana_agregar, font=("Arial", 12))
        entry_nombre.pack(pady=5)
        
        ttk.Label(ventana_agregar, text="Persona de contacto:").pack(pady=5)
        entry_contacto = ttk.Entry(ventana_agregar, font=("Arial", 12))
        entry_contacto.pack(pady=5)
        
        ttk.Label(ventana_agregar, text="Teléfono:").pack(pady=5)
        entry_telefono = ttk.Entry(ventana_agregar, font=("Arial", 12))
        entry_telefono.pack(pady=5)
        
        ttk.Label(ventana_agregar, text="Plazo de entrega:").pack(pady=5)
        entry_plazo = ttk.Entry(ventana_agregar, font=("Arial", 12))
        entry_plazo.insert(0, "7 días")
        entry_plazo.pack(pady=5)
        
        def guardar_proveedor():
            nombre = entry_nombre.get().strip()
            contacto = entry_contacto.get().strip()
            
            if not nombre or not contacto:
                messagebox.showwarning("Advertencia", "Nombre y Contacto son obligatorios.")
                return
            
            proveedores[nombre] = Proveedor(
                nombre,
                contacto,
                entry_telefono.get().strip(),
                [],
                entry_plazo.get().strip()
            )
            
            actualizar_lista_proveedores()
            ventana_agregar.destroy()
            messagebox.showinfo("Éxito", "Proveedor agregado correctamente.")
        
        btn_guardar = ttk.Button(ventana_agregar, text="Guardar", command=guardar_proveedor, style='Accion.TButton')
        btn_guardar.pack(pady=10)
    
    btn_agregar = ttk.Button(frame_botones, text="Agregar Proveedor", command=agregar_proveedor, style='Accion.TButton')
    btn_agregar.pack(side=tk.LEFT, padx=5)
    
    actualizar_lista_proveedores()

def gestionar_categorias():
    ventana_categorias = tk.Toplevel(ventana)
    ventana_categorias.title("Gestión de Categorías")
    ventana_categorias.geometry("500x400")
    
    # Marco principal
    frame_principal = ttk.Frame(ventana_categorias)
    frame_principal.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # Lista de categorías
    frame_lista = ttk.Frame(frame_principal)
    frame_lista.pack(fill=tk.BOTH, expand=True)
    
    lista_categorias = tk.Listbox(frame_lista, font=("Arial", 12), selectbackground=COLOR_TERCIARIO)
    scrollbar = ttk.Scrollbar(frame_lista, orient="vertical", command=lista_categorias.yview)
    lista_categorias.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")
    lista_categorias.pack(fill=tk.BOTH, expand=True)
    
    # Botones
    frame_botones = ttk.Frame(frame_principal)
    frame_botones.pack(fill=tk.X, pady=10)
    
    def actualizar_lista_categorias():
        lista_categorias.delete(0, tk.END)
        for categoria in sorted(categorias):
            lista_categorias.insert(tk.END, categoria)
    
    def agregar_categoria():
        categoria = simpledialog.askstring("Agregar Categoría", "Nombre de la nueva categoría:", parent=ventana_categorias)
        if categoria and categoria not in categorias:
            categorias.append(categoria)
            actualizar_lista_categorias()
            combo_categoria['values'] = categorias
            messagebox.showinfo("Éxito", "Categoría agregada correctamente.")
        elif categoria in categorias:
            messagebox.showwarning("Advertencia", "La categoría ya existe.")
    
    def eliminar_categoria():
        seleccionado = lista_categorias.curselection()
        if seleccionado:
            categoria = lista_categorias.get(seleccionado)
            
            # Verificar si hay productos en esta categoría
            productos_en_categoria = [p for p in inventario.values() if p.categoria == categoria]
            if productos_en_categoria:
                messagebox.showerror("Error", 
                    f"No se puede eliminar: Hay {len(productos_en_categoria)} productos en esta categoría.")
                return
                
            respuesta = messagebox.askyesno("Confirmar", 
                          f"¿Está seguro de eliminar la categoría '{categoria}'?")
            if respuesta:
                categorias.remove(categoria)
                actualizar_lista_categorias()
                combo_categoria['values'] = categorias
                messagebox.showinfo("Éxito", "Categoría eliminada correctamente.")
        else:
            messagebox.showwarning("Advertencia", "Seleccione una categoría para eliminar.")
    
    btn_agregar = ttk.Button(frame_botones, text="Agregar", command=agregar_categoria, style='Accion.TButton')
    btn_agregar.pack(side=tk.LEFT, padx=5)
    
    btn_eliminar = ttk.Button(frame_botones, text="Eliminar", command=eliminar_categoria, style='Peligro.TButton')
    btn_eliminar.pack(side=tk.LEFT, padx=5)
    
    actualizar_lista_categorias()

def gestionar_usuarios():
    ventana_usuarios = tk.Toplevel(ventana)
    ventana_usuarios.title("Gestión de Usuarios")
    ventana_usuarios.geometry("900x600")
    
    # Marco principal
    frame_principal = ttk.Frame(ventana_usuarios)
    frame_principal.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # Lista de usuarios
    frame_lista = ttk.Frame(frame_principal)
    frame_lista.pack(fill=tk.BOTH, expand=True)
    
    lista_usuarios = ttk.Treeview(frame_lista, columns=("Usuario", "Rol", "Proveedor"), show="headings")
    lista_usuarios.heading("Usuario", text="Usuario")
    lista_usuarios.heading("Rol", text="Rol")
    lista_usuarios.heading("Proveedor", text="Proveedor Asociado")
    
    lista_usuarios.column("Usuario", width=200)
    lista_usuarios.column("Rol", width=150)
    lista_usuarios.column("Proveedor", width=300)
    
    scrollbar = ttk.Scrollbar(frame_lista, orient="vertical", command=lista_usuarios.yview)
    lista_usuarios.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")
    lista_usuarios.pack(fill=tk.BOTH, expand=True)
    
    # Botones
    frame_botones = ttk.Frame(frame_principal)
    frame_botones.pack(fill=tk.X, pady=10)
    
    def actualizar_lista_usuarios():
        for item in lista_usuarios.get_children():
            lista_usuarios.delete(item)
        
        for username, usuario in usuarios.items():
            lista_usuarios.insert("", "end", values=(
                username,
                usuario.rol,
                usuario.proveedor_asociado if usuario.proveedor_asociado else "N/A"
            ))
    
    def agregar_usuario():
        ventana_agregar = tk.Toplevel(ventana_usuarios)
        ventana_agregar.title("Agregar Usuario")
        ventana_agregar.geometry("400x350")
        ventana_agregar.resizable(False, False)
        
        ttk.Label(ventana_agregar, text="Nombre de usuario:").pack(pady=5)
        entry_username = ttk.Entry(ventana_agregar, font=("Arial", 12))
        entry_username.pack(pady=5)
        
        ttk.Label(ventana_agregar, text="Contraseña:").pack(pady=5)
        entry_password = ttk.Entry(ventana_agregar, show="*", font=("Arial", 12))
        entry_password.pack(pady=5)
        
        ttk.Label(ventana_agregar, text="Confirmar contraseña:").pack(pady=5)
        entry_confirmar = ttk.Entry(ventana_agregar, show="*", font=("Arial", 12))
        entry_confirmar.pack(pady=5)
        
        ttk.Label(ventana_agregar, text="Rol:").pack(pady=5)
        combo_rol = ttk.Combobox(ventana_agregar, values=["admin", "proveedor", "empleado"], font=("Arial", 12))
        combo_rol.pack(pady=5)
        
        ttk.Label(ventana_agregar, text="Proveedor asociado (solo para rol proveedor):").pack(pady=5)
        combo_proveedor = ttk.Combobox(ventana_agregar, values=list(proveedores.keys()), font=("Arial", 12))
        combo_proveedor.pack(pady=5)
        
        def guardar_usuario():
            username = entry_username.get().strip()
            password = entry_password.get()
            confirmar = entry_confirmar.get()
            rol = combo_rol.get()
            proveedor = combo_proveedor.get() if rol == "proveedor" else ""
            
            if not username or not password or not rol:
                messagebox.showwarning("Advertencia", "Usuario, contraseña y rol son obligatorios.")
                return
                
            if password != confirmar:
                messagebox.showwarning("Advertencia", "Las contraseñas no coinciden.")
                return
                
            if rol == "proveedor" and not proveedor:
                messagebox.showwarning("Advertencia", "Debe seleccionar un proveedor para este rol.")
                return

            if username in usuarios:
                messagebox.showwarning("Advertencia", "El usuario ya existe.")
                return
                
            usuarios[username] = Usuario(username, password, rol, proveedor)
            actualizar_lista_usuarios()
            ventana_agregar.destroy()
            messagebox.showinfo("Éxito", "Usuario agregado correctamente.")
        
        btn_guardar = ttk.Button(ventana_agregar, text="Guardar", command=guardar_usuario, style='Accion.TButton')
        btn_guardar.pack(pady=10)
    
    def eliminar_usuario():
        seleccionado = lista_usuarios.selection()
        if not seleccionado:
            messagebox.showwarning("Advertencia", "Seleccione un usuario para eliminar.")
            return
        username = lista_usuarios.item(seleccionado, 'values')[0]
        if username == "admin":
            messagebox.showerror("Error", "No se puede eliminar el usuario administrador principal.")
            return
        respuesta = messagebox.askyesno("Confirmar", f"¿Está seguro de eliminar el usuario '{username}'?")
        if respuesta:
            del usuarios[username]
            actualizar_lista_usuarios()
            messagebox.showinfo("Éxito", "Usuario eliminado correctamente.")
    
    btn_agregar = ttk.Button(frame_botones, text="Agregar Usuario", command=agregar_usuario, style='Accion.TButton')
    btn_agregar.pack(side=tk.LEFT, padx=5)
    btn_eliminar = ttk.Button(frame_botones, text="Eliminar Usuario", command=eliminar_usuario, style='Peligro.TButton')
    btn_eliminar.pack(side=tk.LEFT, padx=5)
    
    actualizar_lista_usuarios()
def gestionar_sucursales():
    ventana_sucursales = tk.Toplevel(ventana)
    ventana_sucursales.title("Gestión de Sucursales")
    ventana_sucursales.geometry("600x400")

    frame = ttk.Frame(ventana_sucursales)
    frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    lista_sucursales = ttk.Treeview(frame, columns=("Nombre", "Dirección", "Empleado"), show="headings")
    lista_sucursales.heading("Nombre", text="Nombre")
    lista_sucursales.heading("Dirección", text="Dirección")
    lista_sucursales.heading("Empleado", text="Empleado Asignado")
    lista_sucursales.pack(fill=tk.BOTH, expand=True)

    def actualizar_lista():
        for item in lista_sucursales.get_children():
            lista_sucursales.delete(item)
        for nombre, suc in sucursales.items():
            lista_sucursales.insert("", "end", values=(suc.nombre, suc.direccion, suc.empleado_asignado or "Ninguno"))

    def agregar_sucursal():
        win = tk.Toplevel(ventana_sucursales)
        win.title("Agregar Sucursal")
        win.geometry("350x200")
        ttk.Label(win, text="Nombre:").pack()
        entry_nombre = ttk.Entry(win)
        entry_nombre.pack()
        ttk.Label(win, text="Dirección:").pack()
        entry_dir = ttk.Entry(win)
        entry_dir.pack()
        def guardar():
            nombre = entry_nombre.get().strip()
            direccion = entry_dir.get().strip()
            if nombre and direccion:
                sucursales[nombre] = Sucursal(nombre, direccion)
                actualizar_lista()
                win.destroy()
        ttk.Button(win, text="Guardar", command=guardar).pack(pady=10)

    def asignar_empleado():
        seleccionado = lista_sucursales.selection()
        if not seleccionado:
            messagebox.showwarning("Advertencia", "Seleccione una sucursal.")
            return
        nombre_suc = lista_sucursales.item(seleccionado, 'values')[0]
        empleados = [u.username for u in usuarios.values() if u.rol == "empleado"]
        if not empleados:
            messagebox.showinfo("Info", "No hay empleados registrados.")
            return
        empleado = simpledialog.askstring("Asignar Empleado", f"Ingrese el usuario del empleado para '{nombre_suc}':\n{empleados}")
        if empleado in empleados:
            sucursales[nombre_suc].empleado_asignado = empleado
            usuarios[empleado].sucursal_asignada = nombre_suc
            actualizar_lista()
        else:
            messagebox.showerror("Error", "Empleado no válido.")

    btns = ttk.Frame(frame)
    btns.pack(fill=tk.X, pady=5)
    ttk.Button(btns, text="Agregar Sucursal", command=agregar_sucursal).pack(side=tk.LEFT, padx=5)
    ttk.Button(btns, text="Asignar Empleado", command=asignar_empleado).pack(side=tk.LEFT, padx=5)

    actualizar_lista()

def mostrar_historial_ventas():
    ventana_historial = tk.Toplevel(ventana)
    ventana_historial.title("Historial de Ventas")
    ventana_historial.geometry("1200x800")
    
    # Marco principal
    frame_principal = ttk.Frame(ventana_historial)
    frame_principal.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # Filtros
    frame_filtros = ttk.Frame(frame_principal)
    frame_filtros.pack(fill=tk.X, pady=10)
    
    ttk.Label(frame_filtros, text="Filtrar por:").pack(side=tk.LEFT, padx=5)
    
    # Filtro por fecha
    ttk.Label(frame_filtros, text="Desde:").pack(side=tk.LEFT, padx=5)
    entry_desde = ttk.Entry(frame_filtros, width=10)
    entry_desde.pack(side=tk.LEFT, padx=5)
    
    ttk.Label(frame_filtros, text="Hasta:").pack(side=tk.LEFT, padx=5)
    entry_hasta = ttk.Entry(frame_filtros, width=10)
    entry_hasta.pack(side=tk.LEFT, padx=5)
    
    # Filtro por vendedor
    ttk.Label(frame_filtros, text="Vendedor:").pack(side=tk.LEFT, padx=5)
    combo_vendedor = ttk.Combobox(frame_filtros, values=list(usuarios.keys()), width=15)
    combo_vendedor.pack(side=tk.LEFT, padx=5)
    
    # Filtro por método de pago
    ttk.Label(frame_filtros, text="Método:").pack(side=tk.LEFT, padx=5)
    combo_metodo = ttk.Combobox(frame_filtros, values=["Todos", "Efectivo", "Tarjeta", "Transferencia", "QR"], width=12)
    combo_metodo.set("Todos")
    combo_metodo.pack(side=tk.LEFT, padx=5)
    
    def aplicar_filtros():
        fecha_desde = entry_desde.get()
        fecha_hasta = entry_hasta.get()
        vendedor = combo_vendedor.get()
        metodo = combo_metodo.get() if combo_metodo.get() != "Todos" else ""
        
        ventas_filtradas = ventas
        
        # Filtrar por fecha
        if fecha_desde or fecha_hasta:
            try:
                ventas_filtradas = []
                for venta in ventas:
                    venta_date = datetime.strptime(venta.fecha.split()[0], "%Y-%m-%d")
                    
                    cumple_desde = True
                    if fecha_desde:
                        desde_date = datetime.strptime(fecha_desde, "%Y-%m-%d")
                        cumple_desde = venta_date >= desde_date
                    
                    cumple_hasta = True
                    if fecha_hasta:
                        hasta_date = datetime.strptime(fecha_hasta, "%Y-%m-%d")
                        cumple_hasta = venta_date <= hasta_date
                    
                    if cumple_desde and cumple_hasta:
                        ventas_filtradas.append(venta)
            except ValueError:
                messagebox.showerror("Error", "Formato de fecha incorrecto. Use YYYY-MM-DD.")
                return
        
        # Filtrar por vendedor
        if vendedor:
            ventas_filtradas = [v for v in ventas_filtradas if v.vendedor == vendedor]
        
        # Filtrar por método de pago
        if metodo:
            ventas_filtradas = [v for v in ventas_filtradas if v.metodo_pago == metodo]
        
        # Actualizar lista
        for item in lista_historial.get_children():
            lista_historial.delete(item)
        
        for venta in sorted(ventas_filtradas, key=lambda x: x.fecha, reverse=True):
            lista_historial.insert("", "end", values=(
                venta.fecha,
                venta.cliente,
                f"Bs {venta.total:.2f}",
                venta.metodo_pago,
                venta.vendedor
            ))
        
        # Actualizar estadísticas
        total_ventas = sum(v.total for v in ventas_filtradas)
        label_estadisticas.config(text=f"Total ventas: {len(ventas_filtradas)} - Monto total: Bs {total_ventas:.2f}")
    
    btn_filtrar = ttk.Button(frame_filtros, text="Aplicar Filtros", command=aplicar_filtros, style='Accion.TButton')
    btn_filtrar.pack(side=tk.LEFT, padx=10)
    
    # Estadísticas
    label_estadisticas = ttk.Label(frame_principal, text="", font=("Arial", 12, "bold"))
    label_estadisticas.pack(pady=5)
    
    # Lista de ventas
    frame_lista = ttk.Frame(frame_principal)
    frame_lista.pack(fill=tk.BOTH, expand=True)
    
    lista_historial = ttk.Treeview(frame_lista, columns=("Fecha", "Cliente", "Total", "Método", "Vendedor"), show="headings")
    lista_historial.heading("Fecha", text="Fecha")
    lista_historial.heading("Cliente", text="Cliente")
    lista_historial.heading("Total", text="Total")
    lista_historial.heading("Método", text="Método Pago")
    lista_historial.heading("Vendedor", text="Vendedor")
    
    lista_historial.column("Fecha", width=150)
    lista_historial.column("Cliente", width=200)
    lista_historial.column("Total", width=100)
    lista_historial.column("Método", width=100)
    lista_historial.column("Vendedor", width=150)
    
    scrollbar = ttk.Scrollbar(frame_lista, orient="vertical", command=lista_historial.yview)
    lista_historial.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")
    lista_historial.pack(fill=tk.BOTH, expand=True)
    
    # Botones adicionales
    frame_botones = ttk.Frame(frame_principal)
    frame_botones.pack(fill=tk.X, pady=10)
    
    def ver_detalle_venta():
        seleccionado = lista_historial.selection()
        if seleccionado:
            fecha = lista_historial.item(seleccionado, 'values')[0]
            cliente = lista_historial.item(seleccionado, 'values')[1]
            
            # Buscar la venta correspondiente
            venta_seleccionada = None
            for venta in ventas:
                if venta.fecha == fecha and venta.cliente == cliente:
                    venta_seleccionada = venta
                    break
            
            if venta_seleccionada:
                ventana_detalle = tk.Toplevel(ventana_historial)
                ventana_detalle.title(f"Detalle de Venta - {fecha}")
                ventana_detalle.geometry("600x500")
                
                texto = scrolledtext.ScrolledText(ventana_detalle, width=80, height=30, font=("Courier", 10))
                texto.pack(fill=tk.BOTH, expand=True)
                
                texto.insert(tk.END, f"Detalle de Venta - {fecha}\n")
                texto.insert(tk.END, f"Cliente: {venta_seleccionada.cliente}\n")
                texto.insert(tk.END, f"Vendedor: {venta_seleccionada.vendedor}\n")
                texto.insert(tk.END, f"Método de pago: {venta_seleccionada.metodo_pago}\n")
                
                if venta_seleccionada.metodo_pago == "Efectivo":
                    texto.insert(tk.END, f"Monto recibido: Bs {venta_seleccionada.monto_recibido:.2f}\n")
                    texto.insert(tk.END, f"Cambio: Bs {venta_seleccionada.cambio:.2f}\n")
                
                texto.insert(tk.END, "-"*80 + "\n")
                texto.insert(tk.END, "Productos:\n")
                
                for producto, datos in venta_seleccionada.productos.items():
                    texto.insert(tk.END, f"- {producto}: {datos['cantidad']} x Bs {datos['precio']:.2f} = Bs {datos['cantidad'] * datos['precio']:.2f}\n")
                
                texto.insert(tk.END, "-"*80 + "\n")
                texto.insert(tk.END, f"TOTAL: Bs {venta_seleccionada.total:.2f}\n")
                
                texto.config(state=tk.DISABLED)
        else:
            messagebox.showwarning("Advertencia", "Seleccione una venta para ver el detalle.")
    
    btn_detalle = ttk.Button(frame_botones, text="Ver Detalle", command=ver_detalle_venta, style='Accion.TButton')
    btn_detalle.pack(side=tk.LEFT, padx=5)
    
    btn_exportar = ttk.Button(frame_botones, text="Exportar a Excel", command=lambda: exportar_historial_excel(lista_historial))
    btn_exportar.pack(side=tk.LEFT, padx=5)
    
    # Aplicar filtros iniciales
    aplicar_filtros()

def exportar_historial_excel(lista):
    try:
        import pandas as pd
        
        # Obtener datos de la lista
        datos = []
        for item in lista.get_children():
            datos.append(lista.item(item, 'values'))
        
        # Crear DataFrame
        df = pd.DataFrame(datos, columns=["Fecha", "Cliente", "Total", "Método Pago", "Vendedor"])
        
        # Convertir Total a numérico
        df['Total'] = df['Total'].str.replace('Bs ', '').astype(float)
        
        # Guardar archivo
        archivo = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Archivos Excel", "*.xlsx"), ("Todos los archivos", "*.*")],
            title="Guardar historial como"
        )
        
        if archivo:
            df.to_excel(archivo, index=False)
            messagebox.showinfo("Éxito", f"Historial exportado correctamente a:\n{archivo}")
    except ImportError:
        messagebox.showerror("Error", "Para exportar a Excel, necesitas instalar la librería pandas:\npip install pandas")
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo exportar el historial:\n{str(e)}")

# ================= FUNCIONES DE REPORTES =================
def generar_reporte_inventario():
    ventana_reporte = tk.Toplevel(ventana)
    ventana_reporte.title("Generar Reporte de Inventario")
    ventana_reporte.geometry("400x300")
    ventana_reporte.resizable(False, False)
    
    ttk.Label(ventana_reporte, text="Opciones de Reporte", font=("Arial", 14, "bold")).pack(pady=10)
    
    # Opciones
    ttk.Label(ventana_reporte, text="Tipo de reporte:").pack()
    tipo_reporte = ttk.Combobox(ventana_reporte, values=["Completo", "Solo stock bajo", "Por categoría"], font=("Arial", 12))
    tipo_reporte.pack(pady=5)
    
    ttk.Label(ventana_reporte, text="Formato:").pack()
    formato = ttk.Combobox(ventana_reporte, values=["PDF", "CSV", "Pantalla"], font=("Arial", 12))
    formato.pack(pady=5)
    
    def generar():
        tipo = tipo_reporte.get()
        formato_seleccionado = formato.get()
        
        if not tipo or not formato_seleccionado:
            messagebox.showwarning("Advertencia", "Seleccione tipo y formato de reporte.")
            return
        
        # Filtrar productos según el tipo de reporte
        productos_reporte = []
        if tipo == "Completo":
            productos_reporte = list(inventario.values())
        elif tipo == "Solo stock bajo":
            productos_reporte = [p for p in inventario.values() if p.cantidad < p.minimo]
        elif tipo == "Por categoría":
            categoria = simpledialog.askstring("Categoría", "Ingrese la categoría a reportar:", parent=ventana_reporte)
            if categoria:
                productos_reporte = [p for p in inventario.values() if p.categoria.lower() == categoria.lower()]
            else:
                return
        
        if formato_seleccionado == "PDF":
            generar_pdf_inventario(productos_reporte, tipo)
        elif formato_seleccionado == "CSV":
            generar_csv_inventario(productos_reporte, tipo)
        else:  # Pantalla
            mostrar_reporte_pantalla(productos_reporte, tipo)
    
    btn_generar = ttk.Button(ventana_reporte, text="Generar Reporte", command=generar, style='Accion.TButton')
    btn_generar.pack(pady=20)

def generar_pdf_inventario(productos, tipo_reporte):
    archivo = filedialog.asksaveasfilename(
        defaultextension=".pdf",
        filetypes=[("Archivos PDF", "*.pdf"), ("Todos los archivos", "*.*")],
        title="Guardar reporte como"
    )
    if not archivo:
        return
    
    try:
        c = canvas.Canvas(archivo, pagesize=letter)
        width, height = letter
        
        # Encabezado
        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, height - 50, "Reporte de Inventario")
        c.setFont("Helvetica", 12)
        c.drawString(50, height - 80, f"Tipo: {tipo_reporte}")
        c.drawString(50, height - 100, f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        c.drawString(50, height - 120, f"Total productos: {len(productos)}")
        
        # Tabla de productos
        c.setFont("Helvetica-Bold", 10)
        c.drawString(50, height - 150, "Producto")
        c.drawString(250, height - 150, "Cantidad")
        c.drawString(350, height - 150, "Precio")
        c.drawString(450, height - 150, "Categoría")
        
        y_position = height - 170
        c.setFont("Helvetica", 10)
        
        for producto in sorted(productos, key=lambda x: x.nombre):
            if y_position < 100:  # Nueva página si es necesario
                c.showPage()
                y_position = height - 50
                c.setFont("Helvetica", 10)
            
            c.drawString(50, y_position, producto.nombre[:30])
            c.drawString(250, y_position, str(producto.cantidad))
            c.drawString(350, y_position, f"{producto.precio:.2f}")
            c.drawString(450, y_position, producto.categoria)
            
            y_position -= 20
        
        c.save()
        messagebox.showinfo("Éxito", f"Reporte generado en:\n{archivo}")
        webbrowser.open(archivo)
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo generar el PDF:\n{str(e)}")

def generar_csv_inventario(productos, tipo_reporte):
    archivo = filedialog.asksaveasfilename(
        defaultextension=".csv",
        filetypes=[("Archivos CSV", "*.csv"), ("Todos los archivos", "*.*")],
        title="Guardar reporte como"
    )
    if not archivo:
        return
    
    try:
        with open(archivo, 'w', encoding='utf-8') as f:
            f.write("Producto,Cantidad,Precio,Categoría,Proveedor,Stock Mínimo\n")
            for producto in sorted(productos, key=lambda x: x.nombre):
                f.write(f'"{producto.nombre}",{producto.cantidad},{producto.precio},'
                       f'"{producto.categoria}","{producto.proveedor}",{producto.minimo}\n')
        
        messagebox.showinfo("Éxito", f"Reporte generado en:\n{archivo}")
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo generar el CSV:\n{str(e)}")

def mostrar_reporte_pantalla(productos, tipo_reporte):
    ventana_reporte = tk.Toplevel(ventana)
    ventana_reporte.title(f"Reporte de Inventario - {tipo_reporte}")
    ventana_reporte.geometry("800x600")
    
    texto = scrolledtext.ScrolledText(ventana_reporte, width=100, height=30, font=("Courier", 10))
    texto.pack(fill=tk.BOTH, expand=True)
    
    texto.insert(tk.END, f"Reporte de Inventario - {tipo_reporte}\n")
    texto.insert(tk.END, f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
    texto.insert(tk.END, f"Total productos: {len(productos)}\n\n")
    
    texto.insert(tk.END, "Producto                     Cantidad   Precio   Categoría       Proveedor\n")
    texto.insert(tk.END, "-"*80 + "\n")
    
    for producto in sorted(productos, key=lambda x: x.nombre):
        texto.insert(tk.END, f"{producto.nombre[:30]:<30} {producto.cantidad:>8} {producto.precio:>8.2f} "
                      f"{producto.categoria[:15]:<15} {producto.proveedor[:20]}\n")
    
    texto.config(state=tk.DISABLED)
    
    ttk.Button(ventana_reporte, text="Exportar a PDF", 
              command=lambda: generar_pdf_inventario(productos, tipo_reporte)).pack(pady=5)
    ttk.Button(ventana_reporte, text="Exportar a CSV", 
              command=lambda: generar_csv_inventario(productos, tipo_reporte)).pack(pady=5)

def generar_reporte_ventas():
    ventana_reporte = tk.Toplevel(ventana)
    ventana_reporte.title("Generar Reporte de Ventas")
    ventana_reporte.geometry("400x300")
    ventana_reporte.resizable(False, False)
    
    ttk.Label(ventana_reporte, text="Opciones de Reporte", font=("Arial", 14, "bold")).pack(pady=10)
    
    # Opciones de fecha
    ttk.Label(ventana_reporte, text="Desde (YYYY-MM-DD):").pack()
    entry_desde = ttk.Entry(ventana_reporte, font=("Arial", 12))
    entry_desde.pack(pady=5)
    
    ttk.Label(ventana_reporte, text="Hasta (YYYY-MM-DD):").pack()
    entry_hasta = ttk.Entry(ventana_reporte, font=("Arial", 12))
    entry_hasta.pack(pady=5)
    
    ttk.Label(ventana_reporte, text="Formato:").pack()
    formato = ttk.Combobox(ventana_reporte, values=["PDF", "CSV", "Pantalla"], font=("Arial", 12))
    formato.pack(pady=5)
    
    def generar():
        fecha_desde = entry_desde.get()
        fecha_hasta = entry_hasta.get()
        formato_seleccionado = formato.get()
        
        if not formato_seleccionado:
            messagebox.showwarning("Advertencia", "Seleccione un formato de reporte.")
            return
        
        # Filtrar ventas por fecha si se especificó
        ventas_filtradas = ventas
        if fecha_desde or fecha_hasta:
            try:
                ventas_filtradas = []
                for venta in ventas:
                    venta_date = datetime.strptime(venta.fecha.split()[0], "%Y-%m-%d")
                    
                    cumple_desde = True
                    if fecha_desde:
                        desde_date = datetime.strptime(fecha_desde, "%Y-%m-%d")
                        cumple_desde = venta_date >= desde_date
                    
                    cumple_hasta = True
                    if fecha_hasta:
                        hasta_date = datetime.strptime(fecha_hasta, "%Y-%m-%d")
                        cumple_hasta = venta_date <= hasta_date
                    
                    if cumple_desde and cumple_hasta:
                        ventas_filtradas.append(venta)
            except ValueError:
                messagebox.showerror("Error", "Formato de fecha incorrecto. Use YYYY-MM-DD.")
                return
        
        if formato_seleccionado == "PDF":
            generar_pdf_ventas(ventas_filtradas, fecha_desde, fecha_hasta)
        elif formato_seleccionado == "CSV":
            generar_csv_ventas(ventas_filtradas, fecha_desde, fecha_hasta)
        else:  # Pantalla
            mostrar_reporte_ventas_pantalla(ventas_filtradas, fecha_desde, fecha_hasta)
    
    btn_generar = ttk.Button(ventana_reporte, text="Generar Reporte", command=generar, style='Accion.TButton')
    btn_generar.pack(pady=20)

def generar_pdf_ventas(ventas_filtradas, fecha_desde, fecha_hasta):
    archivo = filedialog.asksaveasfilename(
        defaultextension=".pdf",
        filetypes=[("Archivos PDF", "*.pdf"), ("Todos los archivos", "*.*")],
        title="Guardar reporte como"
    )
    if not archivo:
        return
    
    try:
        c = canvas.Canvas(archivo, pagesize=letter)
        width, height = letter
        
        # Encabezado
        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, height - 50, "Reporte de Ventas")
        c.setFont("Helvetica", 12)
        
        rango_fechas = ""
        if fecha_desde and fecha_hasta:
            rango_fechas = f"Del {fecha_desde} al {fecha_hasta}"
        elif fecha_desde:
            rango_fechas = f"Desde {fecha_desde}"
        elif fecha_hasta:
            rango_fechas = f"Hasta {fecha_hasta}"
        
        c.drawString(50, height - 80, rango_fechas)
        c.drawString(50, height - 100, f"Fecha de generación: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        c.drawString(50, height - 120, f"Total ventas: {len(ventas_filtradas)}")
        
        # Resumen
        total_general = sum(v.total for v in ventas_filtradas)
        c.drawString(50, height - 150, f"Total general: Bs {total_general:.2f}")
        
        # Tabla de ventas
        c.setFont("Helvetica-Bold", 10)
        c.drawString(50, height - 180, "Fecha")
        c.drawString(150, height - 180, "Cliente")
        c.drawString(300, height - 180, "Total")
        c.drawString(400, height - 180, "Método Pago")
        c.drawString(500, height - 180, "Vendedor")
        
        y_position = height - 200
        c.setFont("Helvetica", 10)
        
        for venta in sorted(ventas_filtradas, key=lambda x: x.fecha, reverse=True):
            if y_position < 100:  # Nueva página si es necesario
                c.showPage()
                y_position = height - 50
                c.setFont("Helvetica", 10)
            
            c.drawString(50, y_position, venta.fecha.split()[0])
            c.drawString(150, y_position, venta.cliente[:20])
            c.drawString(300, y_position, f"{venta.total:.2f}")
            c.drawString(400, y_position, venta.metodo_pago)
            c.drawString(500, y_position, venta.vendedor[:15])
            
            y_position -= 20
        
        c.save()
        messagebox.showinfo("Éxito", f"Reporte generado en:\n{archivo}")
        webbrowser.open(archivo)
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo generar el PDF:\n{str(e)}")

def generar_csv_ventas(ventas_filtradas, fecha_desde, fecha_hasta):
    archivo = filedialog.asksaveasfilename(
        defaultextension=".csv",
        filetypes=[("Archivos CSV", "*.csv"), ("Todos los archivos", "*.*")],
        title="Guardar reporte como"
    )
    if not archivo:
        return
    
    try:
        with open(archivo, 'w', encoding='utf-8') as f:
            f.write("Fecha,Cliente,Total,Método Pago,Vendedor\n")
            for venta in sorted(ventas_filtradas, key=lambda x: x.fecha, reverse=True):
                f.write(f'"{venta.fecha}","{venta.cliente}",{venta.total},"{venta.metodo_pago}","{venta.vendedor}"\n')
        
        messagebox.showinfo("Éxito", f"Reporte generado en:\n{archivo}")
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo generar el CSV:\n{str(e)}")

def mostrar_reporte_ventas_pantalla(ventas_filtradas, fecha_desde, fecha_hasta):
    ventana_reporte = tk.Toplevel(ventana)
    ventana_reporte.title("Reporte de Ventas")
    ventana_reporte.geometry("900x600")
    
    texto = scrolledtext.ScrolledText(ventana_reporte, width=120, height=30, font=("Courier", 10))
    texto.pack(fill=tk.BOTH, expand=True)
    
    rango_fechas = ""
    if fecha_desde and fecha_hasta:
        rango_fechas = f"Del {fecha_desde} al {fecha_hasta}"
    elif fecha_desde:
        rango_fechas = f"Desde {fecha_desde}"
    elif fecha_hasta:
        rango_fechas = f"Hasta {fecha_hasta}"
    
    texto.insert(tk.END, f"Reporte de Ventas {rango_fechas}\n")
    texto.insert(tk.END, f"Fecha de generación: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
    texto.insert(tk.END, f"Total ventas: {len(ventas_filtradas)}\n")
    
    total_general = sum(v.total for v in ventas_filtradas)
    texto.insert(tk.END, f"Total general: Bs {total_general:.2f}\n\n")
    
    texto.insert(tk.END, "Fecha       Cliente                Total      Método Pago   Vendedor\n")
    texto.insert(tk.END, "-"*80 + "\n")
    
    for venta in sorted(ventas_filtradas, key=lambda x: x.fecha, reverse=True):
        texto.insert(tk.END, f"{venta.fecha.split()[0]} {venta.cliente[:20]:<20} {venta.total:>9.2f} "
                      f"{venta.metodo_pago:<12} {venta.vendedor[:15]}\n")
    
    texto.config(state=tk.DISABLED)
    
    ttk.Button(ventana_reporte, text="Exportar a PDF", 
              command=lambda: generar_pdf_ventas(ventas_filtradas, fecha_desde, fecha_hasta)).pack(pady=5)
    ttk.Button(ventana_reporte, text="Exportar a CSV", 
              command=lambda: generar_csv_ventas(ventas_filtradas, fecha_desde, fecha_hasta)).pack(pady=5)

# ================= DASHBOARD =================
def mostrar_dashboard():
    # Seleccionar la pestaña de dashboard
    notebook.select(3)
    
    # Limpiar el frame del dashboard
    for widget in frame_dashboard.winfo_children():
        widget.destroy()
    
    # Estadísticas generales
    frame_estadisticas = ttk.Frame(frame_dashboard)
    frame_estadisticas.pack(fill=tk.X, pady=10)
    
    # Total productos
    total_productos = len(inventario)
    ttk.Label(frame_estadisticas, text=f"📦 Productos en inventario: {total_productos}", 
         font=("Arial", 14, "bold")).pack(side=tk.LEFT, padx=20)
    
    # Productos con stock bajo
    productos_bajo_stock = [p for p in inventario.values() if p.cantidad < p.minimo]
    ttk.Label(frame_estadisticas, text=f"⚠️ Stock bajo: {len(productos_bajo_stock)}", 
         font=("Arial", 14, "bold"), foreground=COLOR_ALERTA if len(productos_bajo_stock) > 0 else COLOR_TEXTO).pack(side=tk.LEFT, padx=20)

    
    # Total ventas hoy
    hoy = datetime.now().strftime("%Y-%m-%d")
    ventas_hoy = [v for v in ventas if v.fecha.startswith(hoy)]
    ttk.Label(frame_estadisticas, text=f"🛒 Ventas hoy: {len(ventas_hoy)}", 
        font=("Arial", 14, "bold")).pack(side=tk.LEFT, padx=20)
    
    # Total ingresos hoy
    ingresos_hoy = sum(v.total for v in ventas_hoy)
    ttk.Label(frame_estadisticas, text=f"💰 Ingresos hoy: Bs {ingresos_hoy:.2f}", 
         font=("Arial", 14, "bold")).pack(side=tk.LEFT, padx=20)
    
    # Gráficos
    frame_graficos = ttk.Frame(frame_dashboard)
    frame_graficos.pack(fill=tk.BOTH, expand=True, pady=10)
    
    # Gráfico de ventas por día (últimos 7 días)
    frame_ventas = ttk.Frame(frame_graficos)
    frame_ventas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)
    
    ttk.Label(frame_ventas, text="Ventas últimos 7 días", font=("Arial", 12, "bold")).pack()
    
    fechas = []
    totals = []
    for i in range(7):
        fecha = (datetime.now() - timedelta(days=6-i)).strftime("%Y-%m-%d")
        total = sum(v.total for v in ventas if v.fecha.startswith(fecha))
        fechas.append(fecha[5:])  # Solo mes-día
        totals.append(total)
    
    fig, ax = plt.subplots(figsize=(5, 3))
    ax.bar(fechas, totals, color=COLOR_TERCIARIO)
    ax.set_title("Ventas últimos 7 días")
    ax.set_ylabel("Total (Bs)")
    
    canvas_ventas = FigureCanvasTkAgg(fig, master=frame_ventas)
    canvas_ventas.draw()
    canvas_ventas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    # Gráfico de productos más vendidos
    frame_top_productos = ttk.Frame(frame_graficos)
    frame_top_productos.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)
    
    ttk.Label(frame_top_productos, text="Productos más vendidos", font=("Arial", 12, "bold")).pack()
    
    # Contar ventas por producto
    ventas_por_producto = {}
    for venta in ventas:
        for producto, datos in venta.productos.items():
            if producto in ventas_por_producto:
                ventas_por_producto[producto] += datos['cantidad']
            else:
                ventas_por_producto[producto] = datos['cantidad']
    
    # Ordenar y tomar los top 5
    top_productos = sorted(ventas_por_producto.items(), key=lambda x: x[1], reverse=True)[:5]
    nombres = [p[0] for p in top_productos]
    cantidades = [p[1] for p in top_productos]
    
    fig2, ax2 = plt.subplots(figsize=(5, 3))
    ax2.barh(nombres, cantidades, color=COLOR_TERCIARIO)
    ax2.set_title("Top 5 productos más vendidos")
    ax2.set_xlabel("Cantidad vendida")
    
    canvas_productos = FigureCanvasTkAgg(fig2, master=frame_top_productos)
    canvas_productos.draw()
    canvas_productos.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    # Lista de productos con stock bajo
    if len(productos_bajo_stock) > 0:
        frame_stock_bajo = ttk.Frame(frame_dashboard)
        frame_stock_bajo.pack(fill=tk.BOTH, expand=True, pady=10)
        
        ttk.Label(frame_stock_bajo, text="Productos con stock bajo", font=("Arial", 12, "bold"), 
                 foreground=COLOR_ALERTA).pack()
        
        lista_stock_bajo = ttk.Treeview(frame_stock_bajo, columns=("Producto", "Cantidad", "Mínimo"), show="headings")
        lista_stock_bajo.heading("Producto", text="Producto")
        lista_stock_bajo.heading("Cantidad", text="Cantidad")
        lista_stock_bajo.heading("Mínimo", text="Mínimo")
        
        lista_stock_bajo.column("Producto", width=300)
        lista_stock_bajo.column("Cantidad", width=100)
        lista_stock_bajo.column("Mínimo", width=100)
        
        scrollbar = ttk.Scrollbar(frame_stock_bajo, orient="vertical", command=lista_stock_bajo.yview)
        lista_stock_bajo.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        lista_stock_bajo.pack(fill=tk.BOTH, expand=True)
        
        for producto in sorted(productos_bajo_stock, key=lambda x: x.cantidad):
            lista_stock_bajo.insert("", "end", values=(
                producto.nombre,
                producto.cantidad,
                producto.minimo
            ))

    # Botón para activar/desactivar Wilson (solo admin)
    def toggle_wilson():
        global asistente_activo, hilo_wilson
        if not asistente_activo:
            asistente_activo = True
            btn_wilson.config(text="Desactivar Wilson")
            hilo_wilson = threading.Thread(target=escuchar_comandos, daemon=True)
            hilo_wilson.start()
            hablar("Wilson activado. Te escucho.")
        else:
            asistente_activo = False
            btn_wilson.config(text="Activar Wilson")
            hablar("Wilson desactivado.")

    def escuchar_comandos():
        global asistente_activo
        recognizer = sr.Recognizer()
        mic = sr.Microphone()
        hablar("Wilson listo. Dime tu comando.")

        while asistente_activo:
            with mic as source:
                recognizer.adjust_for_ambient_noise(source)
                print("Escuchando...")
                try:
                    audio = recognizer.listen(source, timeout=5)
                except Exception:
                    continue
            try:
                comando = recognizer.recognize_google(audio, language="es-ES")
                print("Escuchado:", comando)
                procesar_comando(comando)
            except sr.UnknownValueError:
                continue
            except Exception as e:
                print("Error en reconocimiento de voz:", e)

    # Solo mostrar el botón si es admin
    if usuario_actual and usuario_actual.rol == "admin":
        global btn_wilson
        btn_wilson = ttk.Button(frame_dashboard, text="Activar Wilson", command=toggle_wilson, style='Accion.TButton')
        btn_wilson.pack(pady=10)

# ================= FUNCIONES UTILITARIAS =================
def alternar_modo_oscuro():
    global modo_oscuro
    modo_oscuro = not modo_oscuro
    actualizar_tema()

def actualizar_tema():
    if modo_oscuro:
        ventana.configure(bg=COLOR_SECUNDARIO)
        estilo = ttk.Style()
        estilo.theme_use("clam") 
        estilo.configure("TFrame", background=COLOR_SECUNDARIO)
        estilo.configure("TLabel", background=COLOR_SECUNDARIO, foreground=COLOR_TEXTO_CLARO)
        estilo.configure("TNotebook", background=COLOR_SECUNDARIO)
        estilo.configure("TNotebook.Tab", background=COLOR_PRIMARIO, foreground=COLOR_TEXTO_CLARO)
        estilo.configure("Treeview", background="#3d3d3d", fieldbackground="#3d3d3d", foreground="white")
        estilo.map("Treeview", background=[("selected", COLOR_TERCIARIO)])
    else:
        ventana.configure(bg=COLOR_FONDO)
        estilo = ttk.Style()
        estilo.theme_use("clam") 
        estilo.configure("TFrame", background=COLOR_FONDO)
        estilo.configure("TLabel", background=COLOR_FONDO, foreground=COLOR_TEXTO)
        estilo.configure("TNotebook", background=COLOR_FONDO)
        estilo.configure("TNotebook.Tab", background=COLOR_FONDO, foreground=COLOR_TEXTO)
        estilo.configure("Treeview", background="white", fieldbackground="white", foreground="black")
        estilo.map("Treeview", background=[("selected", COLOR_TERCIARIO)])

def mostrar_acerca_de():
    messagebox.showinfo("Acerca de", 
        "Sistema de Inventario y Ventas Avanzado\n"
        "Versión 3.0\n\n"
        "Características:\n"
        "- Gestión completa de inventario\n"
        "- Módulo de ventas con ticket\n"
        "- Registro de clientes y proveedores\n"
        "- Alertas de stock mínimo\n"
        "- Generación de reportes en PDF\n"
        "- Historial de ventas\n"
        "- Dashboard con estadísticas\n\n"
        "© 2023 Todos los derechos reservados")

def exportar_inventario():
    archivo = filedialog.asksaveasfilename(
        defaultextension=".csv",
        filetypes=[("Archivos CSV", "*.csv"), ("Todos los archivos", "*.*")],
        title="Guardar inventario como"
    )
    if archivo:
        try:
            with open(archivo, 'w', encoding='utf-8') as f:
                f.write("Producto,Cantidad,Precio,Categoría,Proveedor,Stock Mínimo\n")
                for nombre, producto in inventario.items():
                    f.write(f'"{nombre}",{producto.cantidad},{producto.precio},{producto.categoria},'
                            f'"{producto.proveedor}",{producto.minimo}\n')
            messagebox.showinfo("Éxito", "Inventario exportado correctamente.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo exportar el inventario:\n{str(e)}")

def importar_inventario():
    archivo = filedialog.askopenfilename(
        filetypes=[("Archivos CSV", "*.csv"), ("Todos los archivos", "*.*")],
        title="Seleccionar archivo de inventario"
    )
    if archivo:
        try:
            with open(archivo, 'r', encoding='utf-8') as f:
                lineas = f.readlines()[1:]  # Saltar encabezado
                for linea in lineas:
                    datos = linea.strip().split(',')
                    nombre = datos[0].strip('"')
                    cantidad = int(datos[1])
                    precio = float(datos[2])
                    categoria = datos[3] if len(datos) > 3 else "General"
                    proveedor = datos[4].strip('"') if len(datos) > 4 else ""
                    minimo = int(datos[5]) if len(datos) > 5 else 5
                    
                    inventario[nombre] = Producto(nombre, cantidad, precio, categoria, proveedor, minimo)
            
            actualizar_lista()
            messagebox.showinfo("Éxito", "Inventario importado correctamente.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo importar el inventario:\n{str(e)}")

def sincronizar_inventario_ventas(proveedor_filtro=None):
    for item in lista_inventario_ventas.get_children():
        lista_inventario_ventas.delete(item)
    
    productos_mostrar = inventario.values()
    if proveedor_filtro:
        productos_mostrar = [p for p in inventario.values() if p.proveedor == proveedor_filtro]
    
    for producto in sorted(productos_mostrar, key=lambda x: x.nombre):
        lista_inventario_ventas.insert("", "end", values=(
            producto.nombre, 
            producto.cantidad,
            f"{producto.precio:.2f}"
        ))

def cargar_datos_ejemplo():
    inventario["Laptop HP"] = Producto("Laptop HP", 10, 4500, "Electrónica", "TecnoImport", 3)
    inventario["Mouse Inalámbrico"] = Producto("Mouse Inalámbrico", 25, 120, "Electrónica", "TecnoImport", 5)
    inventario["Teclado Mecánico"] = Producto("Teclado Mecánico", 15, 350, "Electrónica", "TecnoImport", 4)
    inventario["Monitor 24\""] = Producto("Monitor 24\"", 8, 1200, "Electrónica", "TecnoImport", 2)
    inventario["Arroz 1kg"] = Producto("Arroz 1kg", 50, 8, "Alimentos", "Distribuidora Alimenticia", 10)
    inventario["Aceite 1lt"] = Producto("Aceite 1lt", 30, 12, "Alimentos", "Distribuidora Alimenticia", 8)
    inventario["Leche 1lt"] = Producto("Leche 1lt", 40, 7, "Alimentos", "Lácteos S.A.", 15)
    inventario["Camisa Hombre"] = Producto("Camisa Hombre", 20, 150, "Ropa", "ModaTextil", 5)
    inventario["Pantalón Jeans"] = Producto("Pantalón Jeans", 18, 250, "Ropa", "ModaTextil", 5)
    inventario["Jabón"] = Producto("Jabón", 60, 5, "Hogar", "Productos del Hogar", 20)
    
    proveedores["TecnoImport"] = Proveedor("TecnoImport", "Juan Pérez", "77712345", ["Laptop HP", "Mouse Inalámbrico", "Teclado Mecánico", "Monitor 24\""])
    proveedores["Distribuidora Alimenticia"] = Proveedor("Distribuidora Alimenticia", "María Gómez", "77754321", ["Arroz 1kg", "Aceite 1lt"])
    proveedores["Lácteos S.A."] = Proveedor("Lácteos S.A.", "Carlos Ruiz", "77798765", ["Leche 1lt"])
    proveedores["ModaTextil"] = Proveedor("ModaTextil", "Ana Martínez", "77745678", ["Camisa Hombre", "Pantalón Jeans"])
    proveedores["Productos del Hogar"] = Proveedor("Productos del Hogar", "Luisa Fernández", "77723456", ["Jabón"])
    
    clientes["123456789"] = Cliente("Juan Morales", "123456789", "Av. Siempre Viva 123", "77711111", "juan@example.com")
    clientes["987654321"] = Cliente("María López", "987654321", "Calle Falsa 456", "77722222", "maria@example.com")
    
    usuarios["admin"] = Usuario("admin", "admin123", "admin")
    usuarios["proveedor1"] = Usuario("proveedor1", "proveedor1", "proveedor", "TecnoImport")
    usuarios["empleado1"] = Usuario("empleado1", "empleado1", "empleado")
    
    # Agregar algunas ventas de ejemplo
    hoy = datetime.now().strftime("%Y-%m-%d")
    ayer = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    
    ventas.append(Venta(
        {"Laptop HP": {"cantidad": 1, "precio": 4500, "categoria": "Electrónica"}},
        4500,
        "Juan Morales",
        "Efectivo",
        5000
    ))
    
    ventas.append(Venta(
        {"Mouse Inalámbrico": {"cantidad": 2, "precio": 120, "categoria": "Electrónica"},
         "Teclado Mecánico": {"cantidad": 1, "precio": 350, "categoria": "Electrónica"}},
        590,
        "Consumidor Final",
        "Tarjeta"
    ))
    
    ventas.append(Venta(
        {"Arroz 1kg": {"cantidad": 5, "precio": 8, "categoria": "Alimentos"},
         "Aceite 1lt": {"cantidad": 2, "precio": 12, "categoria": "Alimentos"}},
        64,
        "María López",
        "Efectivo",
        70
    ))


import threading
import speech_recognition as sr
import pyttsx3

asistente_activo = False  # Estado del asistente

def hablar(texto):
    def _hablar():
        engine = pyttsx3.init()
        engine.say(texto)
        engine.runAndWait()
    ventana.after(0, _hablar)

citas = []

def procesar_comando(comando):
    comando = comando.lower()
    respuesta = "No entendí la pregunta."

    if "hora" in comando:
        hora_actual = datetime.now().strftime("%H:%M")
        respuesta = f"La hora actual es {hora_actual}."

    elif "chiste" in comando:
        chistes = [
            "¿Por qué los pájaros no usan Facebook? Porque ya tienen Twitter.",
            "¿Qué le dice una iguana a su hermana gemela? Somos iguanitas.",
            "¿Por qué el libro de matemáticas está triste? Porque tiene demasiados problemas.",
            "¿Qué hace una abeja en el gimnasio? ¡Zum-ba!",
            "¿Por qué el tomate se puso rojo? Porque vio a la ensalada desnuda."
        ]
        respuesta = random.choice(chistes)

    elif "agenda una cita" in comando or "agendar cita" in comando or "tengo una cita" in comando:
        import re
        patron = r"(el|para)?\s*(\d{1,2}/\d{1,2}/\d{2,4})?\s*(a las)?\s*(\d{1,2}(:\d{2})?)?"
        match = re.search(patron, comando)
        if match:
            fecha = match.group(2) or datetime.now().strftime("%d/%m/%Y")
            hora = match.group(4) or "sin hora"
            citas.append(f"Cita el {fecha} a las {hora}")
            respuesta = f"Cita agendada para el {fecha} a las {hora}."
        else:
            respuesta = "¿Para qué día y hora quieres agendar la cita?"

    elif "mis citas" in comando or "ver citas" in comando:
        if citas:
            respuesta = "Tus próximas citas son: " + "; ".join(citas)
        else:
            respuesta = "No tienes citas agendadas."

    elif "pon música de" in comando or "reproduce música de" in comando or "reproduce" in comando:
        if "pon música de" in comando:
            cancion = comando.split("pon música de")[-1].strip()
        elif "reproduce música de" in comando:
            cancion = comando.split("reproduce música de")[-1].strip()
        else:
            cancion = comando.split("reproduce")[-1].strip()
        if cancion:
            url = f"https://www.youtube.com/results?search_query={cancion.replace(' ', '+')}"
            webbrowser.open(url)
            respuesta = f"Reproduciendo {cancion} en YouTube."
        else:
            respuesta = "¿Qué canción quieres escuchar?"

    elif "stock" in comando or "tengo de" in comando:
        for nombre in inventario:
            if nombre.lower() in comando:
                respuesta = f"Stock de {nombre}: {inventario[nombre].cantidad} unidades."
                break
        else:
            respuesta = "No encontré ese producto."

    elif "ganancia" in comando and "hoy" in comando:
        hoy = datetime.now().strftime("%Y-%m-%d")
        ganancia = sum(v.total for v in ventas if v.fecha.startswith(hoy))
        respuesta = f"La ganancia de hoy es: Bs {ganancia:.2f}"

    elif "ventas" in comando and "hoy" in comando:
        hoy = datetime.now().strftime("%Y-%m-%d")
        cantidad = sum(1 for v in ventas if v.fecha.startswith(hoy))
        respuesta = f"Hoy se realizaron {cantidad} ventas."

    elif "más vendido" in comando:
        ventas_por_producto = {}
        for venta in ventas:
            for producto, datos in venta.productos.items():
                ventas_por_producto[producto] = ventas_por_producto.get(producto, 0) + datos['cantidad']
        if ventas_por_producto:
            mas_vendido = max(ventas_por_producto, key=ventas_por_producto.get)
            respuesta = f"El producto más vendido es: {mas_vendido} ({ventas_por_producto[mas_vendido]} unidades)"
        else:
            respuesta = "No hay ventas registradas."

    elif "menos vendido" in comando:
        ventas_por_producto = {}
        for venta in ventas:
            for producto, datos in venta.productos.items():
                ventas_por_producto[producto] = ventas_por_producto.get(producto, 0) + datos['cantidad']
        if ventas_por_producto:
            menos_vendido = min(ventas_por_producto, key=ventas_por_producto.get)
            respuesta = f"El producto menos vendido es: {menos_vendido} ({ventas_por_producto[menos_vendido]} unidades)"
        else:
            respuesta = "No hay ventas registradas."

    elif "desactívate" in comando or "desactivate" in comando:
        global asistente_activo
        asistente_activo = False
        respuesta = "Wilson desactivado. Dime 'hey wilson' para volver a activarme."

    elif "hola" in comando or "buenos días" in comando or "buenas tardes" in comando:
        respuesta = "¡Hola! ¿En qué puedo ayudarte?"

    elif "ayuda" in comando or "puedes hacer" in comando:
        respuesta = ("Puedes preguntarme cosas como: "
                     "¿Cuánto tengo de [producto]? ¿Cuál es mi ganancia hoy? "
                     "¿Cuántas ventas hice hoy? ¿Cuál es el producto más vendido? "
                     "Pídeme la hora, un chiste, agenda una cita o pon música de YouTube.")

    hablar(respuesta)



   
#     iniciar_asistente_voz()

# ================= INTERFAZ PRINCIPAL =================
ventana = tk.Tk()
ventana.title("Sistema de Gestión de Inventario y Ventas Avanzado")
ventana.geometry("1200x800")
ventana.configure(bg=COLOR_FONDO)

# Configurar para guardar datos al cerrar
def on_closing():
    guardar_datos()
    ventana.destroy()

ventana.protocol("WM_DELETE_WINDOW", on_closing)

# Menú principal
menubar = tk.Menu(ventana)

# Menú Archivo
menu_archivo = tk.Menu(menubar, tearoff=0)
menu_archivo.add_command(label="Importar Inventario", command=importar_inventario)
menu_archivo.add_command(label="Exportar Inventario", command=exportar_inventario)
menu_archivo.add_separator()
menu_archivo.add_command(label="Alternar Modo Oscuro", command=alternar_modo_oscuro)
menu_archivo.add_separator()
menu_archivo.add_command(label="Salir", command=on_closing)
menubar.add_cascade(label="Archivo", menu=menu_archivo)

# Menú Gestión
menu_gestion = tk.Menu(menubar, tearoff=0)
menu_gestion.add_command(label="Clientes", command=gestionar_clientes)
menu_gestion.add_command(label="Proveedores", command=gestionar_proveedores)
menu_gestion.add_command(label="Categorías", command=gestionar_categorias)
menu_gestion.add_command(label="Usuarios", command=gestionar_usuarios)
menu_gestion.add_command(label="Historial de Ventas", command=mostrar_historial_ventas)
menubar.add_cascade(label="Gestión", menu=menu_gestion)
menu_gestion.add_command(label="Sucursales", command=gestionar_sucursales)

# Menú Reportes
menu_reportes = tk.Menu(menubar, tearoff=0)
menu_reportes.add_command(label="Reporte de Inventario", command=generar_reporte_inventario)
menu_reportes.add_command(label="Reporte de Ventas", command=generar_reporte_ventas)
menubar.add_cascade(label="Reportes", menu=menu_reportes)

# Menú Ayuda
menu_ayuda = tk.Menu(menubar, tearoff=0)
menu_ayuda.add_command(label="Acerca de...", command=mostrar_acerca_de)

menubar.add_cascade(label="Ayuda", menu=menu_ayuda)

ventana.config(menu=menubar)

# Estilo
estilo = ttk.Style()
estilo.theme_use("clam")

# Configurar estilos
estilo.configure("TFrame", background=COLOR_FONDO)
estilo.configure("TLabel", background=COLOR_FONDO, foreground=COLOR_TEXTO, font=("Arial", 10))
estilo.configure("TButton", background=COLOR_TERCIARIO, foreground=COLOR_TEXTO_CLARO, 
                font=("Arial", 10, "bold"), padding=5)
estilo.configure("Accion.TButton", background=COLOR_EXITO, foreground=COLOR_TEXTO_CLARO)
estilo.configure("Peligro.TButton", background=COLOR_ALERTA, foreground=COLOR_TEXTO_CLARO)
estilo.map("TButton", background=[("active", "#2980b9")])
estilo.map("Accion.TButton", background=[("active", "#27ae60")])
estilo.map("Peligro.TButton", background=[("active", "#c0392b")])

# Notebook (pestañas)
notebook = ttk.Notebook(ventana)
notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

# Pestaña de Inventario
tab_inventario = ttk.Frame(notebook)
notebook.add(tab_inventario, text="Inventario")

# Marco para los campos de entrada en inventario
marco_entradas = ttk.Frame(tab_inventario, padding="10")
marco_entradas.pack(fill=tk.X, padx=10, pady=10)

# Campos de entrada
ttk.Label(marco_entradas, text="Nombre del producto:").grid(row=0, column=0, sticky=tk.W, pady=2)
entry_nombre = ttk.Entry(marco_entradas, width=30, font=("Arial", 10))
entry_nombre.grid(row=0, column=1, sticky=tk.W, pady=2)

ttk.Label(marco_entradas, text="Cantidad:").grid(row=1, column=0, sticky=tk.W, pady=2)
entry_cantidad = ttk.Entry(marco_entradas, width=10, font=("Arial", 10))
entry_cantidad.grid(row=1, column=1, sticky=tk.W, pady=2)

ttk.Label(marco_entradas, text="Precio por unidad (Bs):").grid(row=2, column=0, sticky=tk.W, pady=2)
entry_precio = ttk.Entry(marco_entradas, width=10, font=("Arial", 10))
entry_precio.grid(row=2, column=1, sticky=tk.W, pady=2)

ttk.Label(marco_entradas, text="Categoría:").grid(row=0, column=2, sticky=tk.W, padx=10, pady=2)
combo_categoria = ttk.Combobox(marco_entradas, values=categorias, width=15, font=("Arial", 10))
combo_categoria.set("General")
combo_categoria.grid(row=0, column=3, sticky=tk.W, pady=2)

# ...existing code...
ttk.Label(marco_entradas, text="Precio de compra (Bs):").grid(row=3, column=0, sticky=tk.W, pady=2)
entry_costo = ttk.Entry(marco_entradas, width=10, font=("Arial", 10))
entry_costo.grid(row=3, column=1, sticky=tk.W, pady=2)
# ...existing code...

ttk.Label(marco_entradas, text="Proveedor:").grid(row=1, column=2, sticky=tk.W, padx=10, pady=2)
combo_proveedor = ttk.Combobox(marco_entradas, width=15, font=("Arial", 10))
combo_proveedor.grid(row=1, column=3, sticky=tk.W, pady=2)

ttk.Label(marco_entradas, text="Stock mínimo:").grid(row=2, column=2, sticky=tk.W, padx=10, pady=2)
entry_minimo = ttk.Entry(marco_entradas, width=10, font=("Arial", 10))
entry_minimo.insert(0, "5")
entry_minimo.grid(row=2, column=3, sticky=tk.W, pady=2)

# Marco para los botones de inventario
marco_botones_inventario = ttk.Frame(tab_inventario, padding="10")
marco_botones_inventario.pack(fill=tk.X, padx=10, pady=5)

# Botones de inventario
# ...en marco_botones_inventario...
ttk.Button(marco_botones_inventario, text="➕ Agregar Producto", command=agregar_producto, style='Accion.TButton').pack(side=tk.LEFT, padx=5)
ttk.Button(marco_botones_inventario, text="✏️ Modificar Producto", command=modificar_producto).pack(side=tk.LEFT, padx=5)
ttk.Button(marco_botones_inventario, text="🗑️ Eliminar Producto", command=eliminar_producto, style='Peligro.TButton').pack(side=tk.LEFT, padx=5)
ttk.Button(marco_botones_inventario, text="🔍 Buscar Producto", command=buscar_producto).pack(side=tk.LEFT, padx=5)
# Marco para la lista de productos en inventario
marco_lista_inventario = ttk.Frame(tab_inventario, padding="10")
marco_lista_inventario.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

# Lista de productos (Treeview)
lista_inventario = ttk.Treeview(marco_lista_inventario, 
                               columns=("Nombre", "Cantidad", "Precio Unitario", "Categoría", "Proveedor", "Mínimo", "Alerta"), 
                               show="headings", selectmode="extended")

# Configurar columnas
lista_inventario.heading("Nombre", text="Nombre del Producto", anchor=tk.W)
lista_inventario.heading("Cantidad", text="Cantidad", anchor=tk.CENTER)
lista_inventario.heading("Precio Unitario", text="Precio Unitario", anchor=tk.CENTER)
lista_inventario.heading("Categoría", text="Categoría", anchor=tk.CENTER)
lista_inventario.heading("Proveedor", text="Proveedor", anchor=tk.CENTER)
lista_inventario.heading("Mínimo", text="Stock Mín", anchor=tk.CENTER)
lista_inventario.heading("Alerta", text="Alerta", anchor=tk.CENTER)

lista_inventario.column("Nombre", width=250, anchor=tk.W)
lista_inventario.column("Cantidad", width=80, anchor=tk.CENTER)
lista_inventario.column("Precio Unitario", width=100, anchor=tk.CENTER)
lista_inventario.column("Categoría", width=100, anchor=tk.CENTER)
lista_inventario.column("Proveedor", width=150, anchor=tk.CENTER)
lista_inventario.column("Mínimo", width=70, anchor=tk.CENTER)
lista_inventario.column("Alerta", width=50, anchor=tk.CENTER)

# Scrollbar
scrollbar_inventario = ttk.Scrollbar(marco_lista_inventario, orient="vertical", command=lista_inventario.yview)
lista_inventario.configure(yscrollcommand=scrollbar_inventario.set)
scrollbar_inventario.pack(side="right", fill="y")
lista_inventario.pack(fill=tk.BOTH, expand=True)

# Pestaña de Ventas
tab_ventas = ttk.Frame(notebook)
notebook.add(tab_ventas, text="Ventas")

# Marco principal de ventas
marco_ventas = ttk.Frame(tab_ventas, padding="10")
marco_ventas.pack(fill=tk.BOTH, expand=True)

# Marco para el inventario en ventas
marco_inventario_ventas = ttk.Frame(marco_ventas, padding="10")
marco_inventario_ventas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
# ...existing code...

# Barra de búsqueda de productos en ventas
frame_busqueda_ventas = ttk.Frame(marco_inventario_ventas)
frame_busqueda_ventas.pack(fill=tk.X, pady=5)

entry_busqueda_ventas = ttk.Entry(frame_busqueda_ventas, width=30, font=("Arial", 10))
entry_busqueda_ventas.pack(side=tk.LEFT, padx=5)

def buscar_producto_ventas():
    texto = entry_busqueda_ventas.get().strip().lower()
    for item in lista_inventario_ventas.get_children():
        lista_inventario_ventas.delete(item)
    productos_mostrar = inventario.values()
    if usuario_actual and usuario_actual.rol == 'proveedor':
        productos_mostrar = [p for p in inventario.values() if p.proveedor == usuario_actual.proveedor_asociado]
    for producto in sorted(productos_mostrar, key=lambda x: x.nombre):
        if texto in producto.nombre.lower():
            lista_inventario_ventas.insert("", "end", values=(
                producto.nombre, 
                producto.cantidad,
                f"{producto.precio:.2f}"
            ))

btn_buscar_ventas = ttk.Button(frame_busqueda_ventas, text="Buscar", command=buscar_producto_ventas)
btn_buscar_ventas.pack(side=tk.LEFT, padx=5)

# Lista de productos en ventas
lista_inventario_ventas = ttk.Treeview(marco_inventario_ventas, 
                                      columns=("Nombre", "Cantidad", "Precio"), 
                                      show="headings", selectmode="browse",
                                      height=20)
# ...resto del código...

# Lista de productos en ventas
lista_inventario_ventas = ttk.Treeview(marco_inventario_ventas, 
                                      columns=("Nombre", "Cantidad", "Precio"), 
                                      show="headings", selectmode="browse",
                                      height=20)

lista_inventario_ventas.heading("Nombre", text="Producto", anchor=tk.W)
lista_inventario_ventas.heading("Cantidad", text="Disponible", anchor=tk.CENTER)
lista_inventario_ventas.heading("Precio", text="Precio", anchor=tk.CENTER)

lista_inventario_ventas.column("Nombre", width=250, anchor=tk.W)
lista_inventario_ventas.column("Cantidad", width=80, anchor=tk.CENTER)
lista_inventario_ventas.column("Precio", width=80, anchor=tk.CENTER)

scrollbar_inventario_ventas = ttk.Scrollbar(marco_inventario_ventas, orient="vertical", 
                                          command=lista_inventario_ventas.yview)
lista_inventario_ventas.configure(yscrollcommand=scrollbar_inventario_ventas.set)
scrollbar_inventario_ventas.pack(side="right", fill="y")
lista_inventario_ventas.pack(fill=tk.BOTH, expand=True)

# Botones de ventas
marco_botones_ventas = ttk.Frame(marco_inventario_ventas, padding="5")
marco_botones_ventas.pack(fill=tk.X, pady=5)

ttk.Button(marco_botones_ventas, text="Agregar al Carrito", style='Accion.TButton',
          command=agregar_al_carrito).pack(side=tk.LEFT, padx=5)

# Marco para el carrito
marco_carrito = ttk.Frame(marco_ventas, padding="10")
marco_carrito.pack(side=tk.LEFT, fill=tk.BOTH)

# Lista del carrito
lista_carrito = ttk.Treeview(marco_carrito, 
                            columns=("Nombre", "Cantidad", "Precio", "Subtotal"), 
                            show="headings", selectmode="browse",
                            height=10)

lista_carrito.heading("Nombre", text="Producto", anchor=tk.W)
lista_carrito.heading("Cantidad", text="Cantidad", anchor=tk.CENTER)
lista_carrito.heading("Precio", text="P. Unitario", anchor=tk.CENTER)
lista_carrito.heading("Subtotal", text="Subtotal", anchor=tk.CENTER)

lista_carrito.column("Nombre", width=200, anchor=tk.W)
lista_carrito.column("Cantidad", width=70, anchor=tk.CENTER)
lista_carrito.column("Precio", width=90, anchor=tk.CENTER)
lista_carrito.column("Subtotal", width=90, anchor=tk.CENTER)

scrollbar_carrito = ttk.Scrollbar(marco_carrito, orient="vertical", 
                                command=lista_carrito.yview)
lista_carrito.configure(yscrollcommand=scrollbar_carrito.set)
scrollbar_carrito.pack(side="right", fill="y")
lista_carrito.pack(fill=tk.BOTH)

# Botones del carrito
marco_botones_carrito = ttk.Frame(marco_carrito, padding="5")
marco_botones_carrito.pack(fill=tk.X, pady=5)

ttk.Button(marco_botones_carrito, text="Eliminar del Carrito", 
          command=eliminar_del_carrito, style='Peligro.TButton').pack(side=tk.LEFT, padx=5)

# Total de la venta
label_total = ttk.Label(marco_carrito, text="Total a Pagar: Bs 0.00", 
                       font=("Arial", 16, "bold"), foreground="#27ae60")
label_total.pack(pady=10)

# Botones finalizar/cancelar venta
marco_acciones_venta = ttk.Frame(marco_carrito, padding="5")
marco_acciones_venta.pack(fill=tk.X, pady=5)

ttk.Button(marco_acciones_venta, text="Finalizar Venta", style='Accion.TButton',
          command=finalizar_venta).pack(side=tk.LEFT, padx=5)
ttk.Button(marco_acciones_venta, text="Cancelar Venta", 
          command=cancelar_venta, style='Peligro.TButton').pack(side=tk.LEFT, padx=5)

# Área del ticket
marco_ticket = ttk.Frame(marco_ventas, padding="10")
marco_ticket.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

ttk.Label(marco_ticket, text="Ticket de Venta", font=("Arial", 12, "bold")).pack()
texto_ticket = scrolledtext.ScrolledText(marco_ticket, width=40, height=20,
                                       font=("Courier", 10), state=tk.DISABLED)
texto_ticket.pack(fill=tk.BOTH, expand=True)

# Botones de ticket
marco_botones_ticket = ttk.Frame(marco_ticket, padding="5")
marco_botones_ticket.pack(fill=tk.X, pady=5)

ttk.Button(marco_botones_ticket, text="Imprimir Ticket", 
          command=imprimir_ticket).pack(side=tk.LEFT, padx=5)
ttk.Button(marco_botones_ticket, text="Guardar Ticket", 
          command=guardar_ticket).pack(side=tk.LEFT, padx=5)

# Pestaña de Reportes
tab_reportes = ttk.Frame(notebook)
notebook.add(tab_reportes, text="Reportes")

# Marco para reportes
marco_reportes = ttk.Frame(tab_reportes, padding="10")
marco_reportes.pack(fill=tk.BOTH, expand=True)

ttk.Label(marco_reportes, text="Generar Reportes", font=("Arial", 14, "bold")).pack(pady=10)

frame_botones_reportes = ttk.Frame(marco_reportes)
frame_botones_reportes.pack(pady=20)

ttk.Button(frame_botones_reportes, text="Reporte de Inventario", 
          command=generar_reporte_inventario, width=25).pack(pady=10)
ttk.Button(frame_botones_reportes, text="Reporte de Ventas", 
          command=generar_reporte_ventas, width=25).pack(pady=10)
ttk.Button(frame_botones_reportes, text="Productos con Stock Bajo", 
          command=lambda: generar_reporte_inventario(), width=25).pack(pady=10)

# Pestaña de Dashboard (solo para admin)
tab_dashboard = ttk.Frame(notebook)
notebook.add(tab_dashboard, text="Dashboard", state='disabled')

frame_dashboard = ttk.Frame(tab_dashboard)
frame_dashboard.pack(fill=tk.BOTH, expand=True)

# Configurar evento para cuando se cambie de pestaña
def on_tab_changed(event):
    if notebook.index(notebook.select()) == 1:  # Si es la pestaña de ventas
        if usuario_actual and usuario_actual.rol == 'proveedor':
            sincronizar_inventario_ventas(usuario_actual.proveedor_asociado)
        else:
            sincronizar_inventario_ventas()
    elif notebook.index(notebook.select()) == 3:  # Si es la pestaña de dashboard
        mostrar_dashboard()

notebook.bind("<<NotebookTabChanged>>", on_tab_changed)

# Cargar datos al iniciar
cargar_datos()

# Mostrar login al iniciar
mostrar_login()

# Actualizar listas
actualizar_lista()
sincronizar_inventario_ventas()

# Actualizar combobox de proveedores
combo_proveedor['values'] = list(proveedores.keys())

# Enfocar el primer campo al iniciar
entry_nombre.focus_set()

# Ejecutar la aplicación
ventana.mainloop()