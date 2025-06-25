import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
from tkinter import scrolledtext
import datetime
import json
import os
from datetime import datetime, timedelta
import random
import webbrowser
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import tempfile

# Configuración de colores - Paleta moderna
COLORES = {
    'primario': '#2c3e50',      # Azul oscuro elegante
    'secundario': '#3498db',    # Azul brillante
    'exito': '#27ae60',         # Verde éxito
    'peligro': '#e74c3c',       # Rojo alerta
    'advertencia': '#f39c12',   # Naranja advertencia
    'fondo': '#ecf0f1',         # Gris claro
    'fondo_oscuro': '#34495e',  # Gris oscuro
    'texto': '#2c3e50',         # Texto principal
    'texto_claro': '#ffffff',   # Texto claro
    'acento': '#9b59b6',        # Púrpura acento
    'sombra': '#bdc3c7',        # Gris sombra
    'tarjeta': '#ffffff',       # Fondo tarjetas
    'hover': '#1abc9c'          # Color hover
}

# Variables globales
inventario = {}
ventas = []
clientes = {}
proveedores = {}
carrito = {}
total_venta = 0.0
usuario_actual = "Administrador"
ARCHIVO_INVENTARIO = "inventario.json"
ARCHIVO_VENTAS = "ventas.json"
ARCHIVO_CLIENTES = "clientes.json"
ARCHIVO_PROVEEDORES = "proveedores.json"

class Producto:
    def __init__(self, nombre, cantidad, precio, categoria="General", proveedor="", minimo=5, 
                 fecha_vencimiento=None, lote=None, ubicacion="Almacén"):
        self.nombre = nombre
        self.cantidad = cantidad
        self.precio = precio
        self.categoria = categoria
        self.proveedor = proveedor
        self.minimo = minimo
        self.fecha_vencimiento = fecha_vencimiento
        self.lote = lote
        self.ubicacion = ubicacion
        self.fecha_actualizacion = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def a_diccionario(self):
        return {
            'nombre': self.nombre,
            'cantidad': self.cantidad,
            'precio': self.precio,
            'categoria': self.categoria,
            'proveedor': self.proveedor,
            'minimo': self.minimo,
            'fecha_vencimiento': self.fecha_vencimiento.strftime("%Y-%m-%d") if self.fecha_vencimiento else None,
            'lote': self.lote,
            'ubicacion': self.ubicacion,
            'fecha_actualizacion': self.fecha_actualizacion
        }
    
    @classmethod
    def desde_diccionario(cls, datos):
        fecha_vencimiento = datetime.strptime(datos['fecha_vencimiento'], "%Y-%m-%d") if datos['fecha_vencimiento'] else None
        return cls(
            datos['nombre'],
            datos['cantidad'],
            datos['precio'],
            datos['categoria'],
            datos['proveedor'],
            datos['minimo'],
            fecha_vencimiento,
            datos['lote'],
            datos['ubicacion']
        )

class Venta:
    def __init__(self, productos, total, cliente="Consumidor Final", metodo_pago="Efectivo"):
        self.productos = productos
        self.total = total
        self.fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.cliente = cliente
        self.metodo_pago = metodo_pago
        self.vendedor = usuario_actual
    
    def a_diccionario(self):
        return {
            'productos': self.productos,
            'total': self.total,
            'fecha': self.fecha,
            'cliente': self.cliente,
            'metodo_pago': self.metodo_pago,
            'vendedor': self.vendedor
        }

class Cliente:
    def __init__(self, nombre, nit, direccion="", telefono="", email=""):
        self.nombre = nombre
        self.nit = nit
        self.direccion = direccion
        self.telefono = telefono
        self.email = email
        self.historial_compras = []
    
    def a_diccionario(self):
        return {
            'nombre': self.nombre,
            'nit': self.nit,
            'direccion': self.direccion,
            'telefono': self.telefono,
            'email': self.email,
            'historial_compras': self.historial_compras
        }

class Proveedor:
    def __init__(self, nombre, contacto, telefono, productos=[], plazo_entrega="7 días"):
        self.nombre = nombre
        self.contacto = contacto
        self.telefono = telefono
        self.productos = productos
        self.plazo_entrega = plazo_entrega
    
    def a_diccionario(self):
        return {
            'nombre': self.nombre,
            'contacto': self.contacto,
            'telefono': self.telefono,
            'productos': self.productos,
            'plazo_entrega': self.plazo_entrega
        }

class InventarioAvanzado:
    def __init__(self):
        self.ventana = tk.Tk()
        self.configurar_ventana()
        self.configurar_estilos()
        self.cargar_datos()
        self.crear_interfaz()
    
    def configurar_ventana(self):
        self.ventana.title("🏪 Sistema de Gestión Empresarial Avanzado")
        self.ventana.geometry("1400x900")
        self.ventana.configure(bg=COLORES['fondo'])
        self.ventana.resizable(True, True)
        self.ventana.state('zoomed' if self.ventana.tk.call('tk', 'windowingsystem') == 'win32' else 'normal')
    
    def configurar_estilos(self):
        self.estilo = ttk.Style()
        self.estilo.theme_use("clam")
        
        # Configurar estilos personalizados
        self.estilo.configure("TFrame", background=COLORES['fondo'])
        self.estilo.configure("TLabel", background=COLORES['fondo'], 
                            font=("Segoe UI", 10), foreground=COLORES['texto'])
        
        # Botones principales
        self.estilo.configure("Primario.TButton", 
                            background=COLORES['primario'],
                            foreground=COLORES['texto_claro'],
                            font=("Segoe UI", 10, "bold"),
                            padding=(15, 8),
                            relief="flat")
        
        # Botones de éxito
        self.estilo.configure("Exito.TButton",
                            background=COLORES['exito'],
                            foreground=COLORES['texto_claro'],
                            font=("Segoe UI", 10, "bold"),
                            padding=(15, 8),
                            relief="flat")
        
        # Botones de peligro
        self.estilo.configure("Peligro.TButton",
                            background=COLORES['peligro'],
                            foreground=COLORES['texto_claro'],
                            font=("Segoe UI", 10, "bold"),
                            padding=(15, 8),
                            relief="flat")
        
        # Botones de advertencia
        self.estilo.configure("Advertencia.TButton",
                            background=COLORES['advertencia'],
                            foreground=COLORES['texto_claro'],
                            font=("Segoe UI", 10, "bold"),
                            padding=(15, 8),
                            relief="flat")
        
        # Entradas de texto
        self.estilo.configure("TEntry",
                            font=("Segoe UI", 11),
                            padding=8,
                            relief="flat",
                            borderwidth=2)
        
        # Notebook (pestañas)
        self.estilo.configure("TNotebook",
                            background=COLORES['fondo'],
                            borderwidth=0)
        self.estilo.configure("TNotebook.Tab",
                            background=COLORES['sombra'],
                            foreground=COLORES['texto'],
                            font=("Segoe UI", 12, "bold"),
                            padding=(20, 12))
        
        # Treeview
        self.estilo.configure("Treeview",
                            background=COLORES['tarjeta'],
                            foreground=COLORES['texto'],
                            font=("Segoe UI", 10),
                            fieldbackground=COLORES['tarjeta'],
                            borderwidth=0,
                            rowheight=35)
        self.estilo.configure("Treeview.Heading",
                            background=COLORES['primario'],
                            foreground=COLORES['texto_claro'],
                            font=("Segoe UI", 11, "bold"),
                            relief="flat")
        
        # Efectos hover
        self.estilo.map("Primario.TButton", 
                       background=[("active", COLORES['secundario'])])
        self.estilo.map("Exito.TButton", 
                       background=[("active", "#229954")])
        self.estilo.map("Peligro.TButton", 
                       background=[("active", "#c0392b")])
        self.estilo.map("Advertencia.TButton", 
                       background=[("active", "#d35400")])
        self.estilo.map("TNotebook.Tab",
                       background=[("selected", COLORES['primario']),
                                 ("active", COLORES['secundario'])],
                       foreground=[("selected", COLORES['texto_claro'])])
    
    def cargar_datos(self):
        try:
            if os.path.exists(ARCHIVO_INVENTARIO):
                with open(ARCHIVO_INVENTARIO, 'r') as f:
                    datos = json.load(f)
                    for nombre, prod_data in datos.items():
                        inventario[nombre] = Producto.desde_diccionario(prod_data)
            
            if os.path.exists(ARCHIVO_VENTAS):
                with open(ARCHIVO_VENTAS, 'r') as f:
                    ventas.extend(json.load(f))
            
            if os.path.exists(ARCHIVO_CLIENTES):
                with open(ARCHIVO_CLIENTES, 'r') as f:
                    clientes_data = json.load(f)
                    for nit, cli_data in clientes_data.items():
                        clientes[nit] = Cliente(
                            cli_data['nombre'],
                            cli_data['nit'],
                            cli_data['direccion'],
                            cli_data['telefono'],
                            cli_data['email']
                        )
                        clientes[nit].historial_compras = cli_data['historial_compras']
            
            if os.path.exists(ARCHIVO_PROVEEDORES):
                with open(ARCHIVO_PROVEEDORES, 'r') as f:
                    proveedores_data = json.load(f)
                    for nombre, prov_data in proveedores_data.items():
                        proveedores[nombre] = Proveedor(
                            prov_data['nombre'],
                            prov_data['contacto'],
                            prov_data['telefono'],
                            prov_data['productos'],
                            prov_data['plazo_entrega']
                        )
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar los datos: {str(e)}")
    
    def guardar_datos(self):
        try:
            # Guardar inventario
            inventario_dict = {nombre: prod.a_diccionario() for nombre, prod in inventario.items()}
            with open(ARCHIVO_INVENTARIO, 'w') as f:
                json.dump(inventario_dict, f, indent=4)
            
            # Guardar ventas
            ventas_dict = [venta.a_diccionario() if hasattr(venta, 'a_diccionario') else venta for venta in ventas]
            with open(ARCHIVO_VENTAS, 'w') as f:
                json.dump(ventas_dict, f, indent=4)
            
            # Guardar clientes
            clientes_dict = {nit: cli.a_diccionario() for nit, cli in clientes.items()}
            with open(ARCHIVO_CLIENTES, 'w') as f:
                json.dump(clientes_dict, f, indent=4)
            
            # Guardar proveedores
            proveedores_dict = {nombre: prov.a_diccionario() for nombre, prov in proveedores.items()}
            with open(ARCHIVO_PROVEEDORES, 'w') as f:
                json.dump(proveedores_dict, f, indent=4)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron guardar los datos: {str(e)}")
    
    def crear_interfaz(self):
        # Header principal
        self.crear_header()
        
        # Contenedor principal
        contenedor_principal = tk.Frame(self.ventana, bg=COLORES['fondo'], 
                                      relief="flat", bd=0)
        contenedor_principal.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Notebook con pestañas
        self.notebook = ttk.Notebook(contenedor_principal)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Crear pestañas
        self.crear_pestana_inventario()
        self.crear_pestana_ventas()
        self.crear_pestana_reportes()
        self.crear_pestana_alertas()
        
        # Footer
        self.crear_footer()
        
        # Eventos
        self.notebook.bind("<<NotebookTabChanged>>", self.on_cambio_pestana)
        
        # Foco inicial
        if hasattr(self, 'entry_nombre'):
            self.entry_nombre.focus_set()
    
    def crear_header(self):
        header = tk.Frame(self.ventana, bg=COLORES['primario'], height=80)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        # Título principal
        titulo = tk.Label(header, 
                         text="🏪 SISTEMA DE GESTIÓN EMPRESARIAL AVANZADO",
                         bg=COLORES['primario'],
                         fg=COLORES['texto_claro'],
                         font=("Segoe UI", 20, "bold"))
        titulo.pack(side=tk.LEFT, padx=30, pady=15)
        
        # Información de fecha y hora
        self.info_fecha = tk.Label(header,
                             text=f"📅 {datetime.now().strftime('%d/%m/%Y - %H:%M')}",
                             bg=COLORES['primario'],
                             fg=COLORES['texto_claro'],
                             font=("Segoe UI", 12))
        self.info_fecha.pack(side=tk.RIGHT, padx=30, pady=25)
        
        # Actualizar hora cada minuto
        self.actualizar_hora()
    
    def actualizar_hora(self):
        ahora = datetime.now().strftime("%d/%m/%Y - %H:%M")
        self.info_fecha.config(text=f"📅 {ahora}")
        self.ventana.after(60000, self.actualizar_hora)  # Actualizar cada minuto
    
    def crear_pestana_inventario(self):
        # Pestaña principal
        self.tab_inventario = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_inventario, text="📦 INVENTARIO")
        
        # Contenedor con padding
        contenedor = tk.Frame(self.tab_inventario, bg=COLORES['fondo'])
        contenedor.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Panel de control (formulario)
        self.crear_panel_control_inventario(contenedor)
        
        # Panel de lista
        self.crear_panel_lista_inventario(contenedor)
    
    def crear_panel_control_inventario(self, padre):
        # Marco del formulario
        marco_form = tk.Frame(padre, bg=COLORES['tarjeta'], relief="raised", bd=2)
        marco_form.pack(fill=tk.X, pady=(0, 20))
        
        # Título del formulario
        titulo_form = tk.Label(marco_form,
                              text="➕ GESTIÓN DE PRODUCTOS",
                              bg=COLORES['tarjeta'],
                              fg=COLORES['primario'],
                              font=("Segoe UI", 16, "bold"))
        titulo_form.pack(pady=20)
        
        # Contenedor de campos
        campos_frame = tk.Frame(marco_form, bg=COLORES['tarjeta'])
        campos_frame.pack(padx=40, pady=20)
        
        # Campo nombre
        tk.Label(campos_frame, text="🏷️ Nombre del Producto:",
                bg=COLORES['tarjeta'], fg=COLORES['texto'],
                font=("Segoe UI", 12, "bold")).grid(row=0, column=0, 
                                                   sticky=tk.W, pady=10, padx=10)
        self.entry_nombre = ttk.Entry(campos_frame, width=30, font=("Segoe UI", 12))
        self.entry_nombre.grid(row=0, column=1, sticky=tk.W, pady=10, padx=10)
        
        # Campo cantidad
        tk.Label(campos_frame, text="📊 Cantidad:",
                bg=COLORES['tarjeta'], fg=COLORES['texto'],
                font=("Segoe UI", 12, "bold")).grid(row=1, column=0, 
                                                   sticky=tk.W, pady=10, padx=10)
        self.entry_cantidad = ttk.Entry(campos_frame, width=15, font=("Segoe UI", 12))
        self.entry_cantidad.grid(row=1, column=1, sticky=tk.W, pady=10, padx=10)
        
        # Campo precio
        tk.Label(campos_frame, text="💰 Precio (Bs):",
                bg=COLORES['tarjeta'], fg=COLORES['texto'],
                font=("Segoe UI", 12, "bold")).grid(row=2, column=0, 
                                                   sticky=tk.W, pady=10, padx=10)
        self.entry_precio = ttk.Entry(campos_frame, width=15, font=("Segoe UI", 12))
        self.entry_precio.grid(row=2, column=1, sticky=tk.W, pady=10, padx=10)
        
        # Campo categoría
        tk.Label(campos_frame, text="🏷️ Categoría:",
                bg=COLORES['tarjeta'], fg=COLORES['texto'],
                font=("Segoe UI", 12, "bold")).grid(row=0, column=2, 
                                                   sticky=tk.W, pady=10, padx=10)
        self.combo_categoria = ttk.Combobox(campos_frame, 
                                          values=["Electrónica", "Alimentos", "Ropa", "Hogar", "Oficina", "General"],
                                          width=15, font=("Segoe UI", 12))
        self.combo_categoria.set("General")
        self.combo_categoria.grid(row=0, column=3, sticky=tk.W, pady=10, padx=10)
        
        # Campo proveedor
        tk.Label(campos_frame, text="🏭 Proveedor:",
                bg=COLORES['tarjeta'], fg=COLORES['texto'],
                font=("Segoe UI", 12, "bold")).grid(row=1, column=2, 
                                                   sticky=tk.W, pady=10, padx=10)
        self.combo_proveedor = ttk.Combobox(campos_frame, 
                                          values=list(proveedores.keys()),
                                          width=15, font=("Segoe UI", 12))
        self.combo_proveedor.grid(row=1, column=3, sticky=tk.W, pady=10, padx=10)
        
        # Campo stock mínimo
        tk.Label(campos_frame, text="⚠️ Stock mínimo:",
                bg=COLORES['tarjeta'], fg=COLORES['texto'],
                font=("Segoe UI", 12, "bold")).grid(row=2, column=2, 
                                                   sticky=tk.W, pady=10, padx=10)
        self.entry_minimo = ttk.Entry(campos_frame, width=15, font=("Segoe UI", 12))
        self.entry_minimo.insert(0, "5")
        self.entry_minimo.grid(row=2, column=3, sticky=tk.W, pady=10, padx=10)
        
        # Campo fecha vencimiento
        tk.Label(campos_frame, text="📅 Fecha Vencimiento (dd/mm/aaaa):",
                bg=COLORES['tarjeta'], fg=COLORES['texto'],
                font=("Segoe UI", 12, "bold")).grid(row=3, column=0, 
                                                   sticky=tk.W, pady=10, padx=10)
        self.entry_vencimiento = ttk.Entry(campos_frame, width=15, font=("Segoe UI", 12))
        self.entry_vencimiento.grid(row=3, column=1, sticky=tk.W, pady=10, padx=10)
        
        # Campo lote
        tk.Label(campos_frame, text="🔢 N° Lote:",
                bg=COLORES['tarjeta'], fg=COLORES['texto'],
                font=("Segoe UI", 12, "bold")).grid(row=3, column=2, 
                                                   sticky=tk.W, pady=10, padx=10)
        self.entry_lote = ttk.Entry(campos_frame, width=15, font=("Segoe UI", 12))
        self.entry_lote.grid(row=3, column=3, sticky=tk.W, pady=10, padx=10)
        
        # Campo ubicación
        tk.Label(campos_frame, text="📍 Ubicación:",
                bg=COLORES['tarjeta'], fg=COLORES['texto'],
                font=("Segoe UI", 12, "bold")).grid(row=4, column=0, 
                                                   sticky=tk.W, pady=10, padx=10)
        self.entry_ubicacion = ttk.Entry(campos_frame, width=15, font=("Segoe UI", 12))
        self.entry_ubicacion.insert(0, "Almacén")
        self.entry_ubicacion.grid(row=4, column=1, sticky=tk.W, pady=10, padx=10)
        
        # Botones de acción
        botones_frame = tk.Frame(marco_form, bg=COLORES['tarjeta'])
        botones_frame.pack(pady=20)
        
        ttk.Button(botones_frame, text="➕ Agregar", 
                  style="Exito.TButton", 
                  command=self.agregar_producto).pack(side=tk.LEFT, padx=10)
        
        ttk.Button(botones_frame, text="🔍 Buscar", 
                  style="Primario.TButton", 
                  command=self.buscar_producto).pack(side=tk.LEFT, padx=10)
        
        ttk.Button(botones_frame, text="🗑️ Eliminar", 
                  style="Peligro.TButton", 
                  command=self.eliminar_producto).pack(side=tk.LEFT, padx=10)
        
        ttk.Button(botones_frame, text="✏️ Modificar", 
                  style="Advertencia.TButton", 
                  command=self.modificar_producto).pack(side=tk.LEFT, padx=10)
        
        ttk.Button(botones_frame, text="📤 Exportar", 
                  style="Primario.TButton", 
                  command=self.exportar_inventario).pack(side=tk.LEFT, padx=10)
        
        ttk.Button(botones_frame, text="📥 Importar", 
                  style="Primario.TButton", 
                  command=self.importar_inventario).pack(side=tk.LEFT, padx=10)
    
    def crear_panel_lista_inventario(self, padre):
        # Marco de la lista
        marco_lista = tk.Frame(padre, bg=COLORES['tarjeta'], relief="raised", bd=2)
        marco_lista.pack(fill=tk.BOTH, expand=True)
        
        # Título de la lista
        titulo_lista = tk.Label(marco_lista,
                               text="📋 INVENTARIO ACTUAL",
                               bg=COLORES['tarjeta'],
                               fg=COLORES['primario'],
                               font=("Segoe UI", 16, "bold"))
        titulo_lista.pack(pady=20)
        
        # Frame para la tabla
        tabla_frame = tk.Frame(marco_lista, bg=COLORES['tarjeta'])
        tabla_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Crear Treeview
        self.lista_inventario = ttk.Treeview(tabla_frame,
                                           columns=("Nombre", "Cantidad", "Precio", "Categoría", "Proveedor", "Mínimo", "Vencimiento", "Lote", "Ubicación", "Alerta"),
                                           show="headings",
                                           selectmode="browse")
        
        # Configurar columnas
        self.lista_inventario.heading("Nombre", text="🏷️ PRODUCTO")
        self.lista_inventario.heading("Cantidad", text="📊 CANTIDAD")
        self.lista_inventario.heading("Precio", text="💰 PRECIO UNIT.")
        self.lista_inventario.heading("Categoría", text="🏷️ CATEGORÍA")
        self.lista_inventario.heading("Proveedor", text="🏭 PROVEEDOR")
        self.lista_inventario.heading("Mínimo", text="⚠️ MÍNIMO")
        self.lista_inventario.heading("Vencimiento", text="📅 VENCIMIENTO")
        self.lista_inventario.heading("Lote", text="🔢 LOTE")
        self.lista_inventario.heading("Ubicación", text="📍 UBICACIÓN")
        self.lista_inventario.heading("Alerta", text="🚨 ALERTA")
        
        self.lista_inventario.column("Nombre", width=200, anchor=tk.W)
        self.lista_inventario.column("Cantidad", width=80, anchor=tk.CENTER)
        self.lista_inventario.column("Precio", width=100, anchor=tk.CENTER)
        self.lista_inventario.column("Categoría", width=120, anchor=tk.CENTER)
        self.lista_inventario.column("Proveedor", width=150, anchor=tk.CENTER)
        self.lista_inventario.column("Mínimo", width=70, anchor=tk.CENTER)
        self.lista_inventario.column("Vencimiento", width=100, anchor=tk.CENTER)
        self.lista_inventario.column("Lote", width=80, anchor=tk.CENTER)
        self.lista_inventario.column("Ubicación", width=100, anchor=tk.CENTER)
        self.lista_inventario.column("Alerta", width=100, anchor=tk.CENTER)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tabla_frame, orient="vertical", 
                                command=self.lista_inventario.yview)
        self.lista_inventario.configure(yscrollcommand=scrollbar.set)
        
        # Empacar elementos
        scrollbar.pack(side="right", fill="y")
        self.lista_inventario.pack(fill=tk.BOTH, expand=True)
    
    def crear_pestana_ventas(self):
        self.tab_ventas = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_ventas, text="💳 VENTAS")
        
        # Contenedor principal
        contenedor = tk.Frame(self.tab_ventas, bg=COLORES['fondo'])
        contenedor.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Dividir en tres secciones
        # Sección izquierda - Inventario disponible
        self.crear_seccion_inventario_ventas(contenedor)
        
        # Sección central - Carrito
        self.crear_seccion_carrito(contenedor)
        
        # Sección derecha - Ticket
        self.crear_seccion_ticket(contenedor)
    
    def crear_seccion_inventario_ventas(self, padre):
        # Marco inventario ventas
        marco_inv = tk.Frame(padre, bg=COLORES['tarjeta'], relief="raised", bd=2)
        marco_inv.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Título
        titulo = tk.Label(marco_inv, text="📦 PRODUCTOS DISPONIBLES",
                         bg=COLORES['tarjeta'], fg=COLORES['primario'],
                         font=("Segoe UI", 14, "bold"))
        titulo.pack(pady=15)
        
        # Lista de productos
        lista_frame = tk.Frame(marco_inv, bg=COLORES['tarjeta'])
        lista_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        self.lista_inventario_ventas = ttk.Treeview(lista_frame,
                                                  columns=("Nombre", "Disponible", "Precio", "Vencimiento"),
                                                  show="headings", height=15)
        
        self.lista_inventario_ventas.heading("Nombre", text="PRODUCTO")
        self.lista_inventario_ventas.heading("Disponible", text="DISPONIBLE")
        self.lista_inventario_ventas.heading("Precio", text="PRECIO")
        self.lista_inventario_ventas.heading("Vencimiento", text="VENCIMIENTO")
        
        self.lista_inventario_ventas.column("Nombre", width=200)
        self.lista_inventario_ventas.column("Disponible", width=80, anchor=tk.CENTER)
        self.lista_inventario_ventas.column("Precio", width=100, anchor=tk.CENTER)
        self.lista_inventario_ventas.column("Vencimiento", width=100, anchor=tk.CENTER)
        
        scrollbar_inv = ttk.Scrollbar(lista_frame, orient="vertical",
                                    command=self.lista_inventario_ventas.yview)
        self.lista_inventario_ventas.configure(yscrollcommand=scrollbar_inv.set)
        
        scrollbar_inv.pack(side="right", fill="y")
        self.lista_inventario_ventas.pack(fill=tk.BOTH, expand=True)
        
        # Botón agregar al carrito
        ttk.Button(marco_inv, text="🛒 AGREGAR AL CARRITO",
                  style="Exito.TButton",
                  command=self.agregar_al_carrito).pack(pady=15)
    
    def crear_seccion_carrito(self, padre):
        # Marco carrito
        marco_carrito = tk.Frame(padre, bg=COLORES['tarjeta'], relief="raised", bd=2)
        marco_carrito.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)
        
        # Título
        titulo = tk.Label(marco_carrito, text="🛒 CARRITO DE COMPRAS",
                         bg=COLORES['tarjeta'], fg=COLORES['primario'],
                         font=("Segoe UI", 14, "bold"))
        titulo.pack(pady=15)
        
        # Lista carrito
        carrito_frame = tk.Frame(marco_carrito, bg=COLORES['tarjeta'])
        carrito_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        self.lista_carrito = ttk.Treeview(carrito_frame,
                                        columns=("Producto", "Cantidad", "Precio", "Subtotal"),
                                        show="headings", height=10)
        
        self.lista_carrito.heading("Producto", text="PRODUCTO")
        self.lista_carrito.heading("Cantidad", text="CANT.")
        self.lista_carrito.heading("Precio", text="PRECIO")
        self.lista_carrito.heading("Subtotal", text="SUBTOTAL")
        
        self.lista_carrito.column("Producto", width=150)
        self.lista_carrito.column("Cantidad", width=60, anchor=tk.CENTER)
        self.lista_carrito.column("Precio", width=80, anchor=tk.CENTER)
        self.lista_carrito.column("Subtotal", width=90, anchor=tk.CENTER)
        
        scrollbar_carrito = ttk.Scrollbar(carrito_frame, orient="vertical",
                                        command=self.lista_carrito.yview)
        self.lista_carrito.configure(yscrollcommand=scrollbar_carrito.set)
        
        scrollbar_carrito.pack(side="right", fill="y")
        self.lista_carrito.pack(fill=tk.BOTH, expand=True)
        
        # Total
        self.label_total = tk.Label(marco_carrito,
                                   text="💵 TOTAL: Bs 0.00",
                                   bg=COLORES['tarjeta'],
                                   fg=COLORES['primario'],
                                   font=("Segoe UI", 16, "bold"))
        self.label_total.pack(pady=10)
        
        # Botones de acción
        botones_frame = tk.Frame(marco_carrito, bg=COLORES['tarjeta'])
        botones_frame.pack(pady=15)
        
        ttk.Button(botones_frame, text="❌ Quitar Item",
                  style="Peligro.TButton",
                  command=self.eliminar_del_carrito).pack(pady=5)
        
        ttk.Button(botones_frame, text="✅ FINALIZAR VENTA",
                  style="Exito.TButton",
                  command=self.finalizar_venta).pack(pady=5)
        
        ttk.Button(botones_frame, text="🚫 Cancelar Venta",
                  style="Advertencia.TButton",
                  command=self.cancelar_venta).pack(pady=5)
    
    def crear_seccion_ticket(self, padre):
        # Marco ticket
        marco_ticket = tk.Frame(padre, bg=COLORES['tarjeta'], relief="raised", bd=2)
        marco_ticket.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        # Título
        titulo = tk.Label(marco_ticket, text="🧾 TICKET DE VENTA",
                         bg=COLORES['tarjeta'], fg=COLORES['primario'],
                         font=("Segoe UI", 14, "bold"))
        titulo.pack(pady=15)
        
        # Área de texto del ticket
        ticket_frame = tk.Frame(marco_ticket, bg=COLORES['tarjeta'])
        ticket_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        self.texto_ticket = scrolledtext.ScrolledText(ticket_frame,
                                                    width=35, height=25,
                                                    font=("Courier New", 10),
                                                    bg=COLORES['fondo'],
                                                    fg=COLORES['texto'],
                                                    state=tk.DISABLED,
                                                    wrap=tk.WORD)
        self.texto_ticket.pack(fill=tk.BOTH, expand=True)
        
        # Botones de ticket
        botones_frame = tk.Frame(marco_ticket, bg=COLORES['tarjeta'])
        botones_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(botones_frame, text="🖨️ Imprimir Ticket",
                  style="Primario.TButton",
                  command=self.imprimir_ticket).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(botones_frame, text="💾 Guardar Ticket",
                  style="Primario.TButton",
                  command=self.guardar_ticket).pack(side=tk.LEFT, padx=5)
    
    def crear_pestana_reportes(self):
        self.tab_reportes = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_reportes, text="📊 REPORTES")
        
        # Contenedor
        contenedor = tk.Frame(self.tab_reportes, bg=COLORES['fondo'])
        contenedor.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Título
        titulo = tk.Label(contenedor,
                         text="📊 REPORTES Y ESTADÍSTICAS",
                         bg=COLORES['fondo'],
                         fg=COLORES['primario'],
                         font=("Segoe UI", 20, "bold"))
        titulo.pack(pady=30)
        
        # Marco de estadísticas
        stats_frame = tk.Frame(contenedor, bg=COLORES['tarjeta'], relief="raised", bd=2)
        stats_frame.pack(fill=tk.X, pady=20)
        
        # Estadísticas rápidas
        self.crear_estadisticas_rapidas(stats_frame)
        
        # Lista de ventas
        self.crear_historial_ventas(contenedor)
    
    def crear_pestana_alertas(self):
        self.tab_alertas = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_alertas, text="🚨 ALERTAS")
        
        # Contenedor
        contenedor = tk.Frame(self.tab_alertas, bg=COLORES['fondo'])
        contenedor.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Título
        titulo = tk.Label(contenedor,
                         text="🚨 ALERTAS Y NOTIFICACIONES",
                         bg=COLORES['fondo'],
                         fg=COLORES['primario'],
                         font=("Segoe UI", 20, "bold"))
        titulo.pack(pady=30)
        
        # Marco de alertas
        marco_alertas = tk.Frame(contenedor, bg=COLORES['tarjeta'], relief="raised", bd=2)
        marco_alertas.pack(fill=tk.BOTH, expand=True, pady=20)
        
        # Título alertas
        titulo_alertas = tk.Label(marco_alertas, text="📢 ALERTAS DE INVENTARIO",
                                 bg=COLORES['tarjeta'], fg=COLORES['primario'],
                                 font=("Segoe UI", 16, "bold"))
        titulo_alertas.pack(pady=20)
        
        # Lista de alertas
        alertas_frame = tk.Frame(marco_alertas, bg=COLORES['tarjeta'])
        alertas_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        self.lista_alertas = ttk.Treeview(alertas_frame,
                                        columns=("Tipo", "Producto", "Detalle", "Acción"),
                                        show="headings")
        
        self.lista_alertas.heading("Tipo", text="TIPO ALERTA")
        self.lista_alertas.heading("Producto", text="PRODUCTO")
        self.lista_alertas.heading("Detalle", text="DETALLE")
        self.lista_alertas.heading("Acción", text="ACCIÓN REQUERIDA")
        
        self.lista_alertas.column("Tipo", width=150, anchor=tk.CENTER)
        self.lista_alertas.column("Producto", width=200)
        self.lista_alertas.column("Detalle", width=300)
        self.lista_alertas.column("Acción", width=200)
        
        scrollbar_alertas = ttk.Scrollbar(alertas_frame, orient="vertical",
                                        command=self.lista_alertas.yview)
        self.lista_alertas.configure(yscrollcommand=scrollbar_alertas.set)
        
        scrollbar_alertas.pack(side="right", fill="y")
        self.lista_alertas.pack(fill=tk.BOTH, expand=True)
        
        # Botón actualizar alertas
        ttk.Button(marco_alertas, text="🔄 Actualizar Alertas",
                  style="Primario.TButton",
                  command=self.actualizar_alertas).pack(pady=20)
    
    def crear_estadisticas_rapidas(self, padre):
        titulo = tk.Label(padre, text="📈 ESTADÍSTICAS RÁPIDAS",
                         bg=COLORES['tarjeta'], fg=COLORES['primario'],
                         font=("Segoe UI", 16, "bold"))
        titulo.pack(pady=20)
        
        stats_container = tk.Frame(padre, bg=COLORES['tarjeta'])
        stats_container.pack(pady=20)
        
        # Estadística 1: Total productos
        stat1 = tk.Frame(stats_container, bg=COLORES['secundario'], 
                        relief="raised", bd=2, padx=20, pady=15)
        stat1.pack(side=tk.LEFT, padx=20)
        
        tk.Label(stat1, text="📦", bg=COLORES['secundario'],
                font=("Segoe UI", 24)).pack()
        self.label_total_productos = tk.Label(stat1, text="0",
                                            bg=COLORES['secundario'],
                                            fg=COLORES['texto_claro'],
                                            font=("Segoe UI", 20, "bold"))
        self.label_total_productos.pack()
        tk.Label(stat1, text="Productos", bg=COLORES['secundario'],
                fg=COLORES['texto_claro'], font=("Segoe UI", 12)).pack()
        
        # Estadística 2: Ventas del día
        stat2 = tk.Frame(stats_container, bg=COLORES['exito'],
                        relief="raised", bd=2, padx=20, pady=15)
        stat2.pack(side=tk.LEFT, padx=20)
        
        tk.Label(stat2, text="💰", bg=COLORES['exito'],
                font=("Segoe UI", 24)).pack()
        self.label_ventas_dia = tk.Label(stat2, text="Bs 0.00",
                                       bg=COLORES['exito'],
                                       fg=COLORES['texto_claro'],
                                       font=("Segoe UI", 16, "bold"))
        self.label_ventas_dia.pack()
        tk.Label(stat2, text="Ventas Hoy", bg=COLORES['exito'],
                fg=COLORES['texto_claro'], font=("Segoe UI", 12)).pack()
        
        # Estadística 3: Total ventas
        stat3 = tk.Frame(stats_container, bg=COLORES['acento'],
                        relief="raised", bd=2, padx=20, pady=15)
        stat3.pack(side=tk.LEFT, padx=20)
        
        tk.Label(stat3, text="🧾", bg=COLORES['acento'],
                font=("Segoe UI", 24)).pack()
        self.label_total_ventas = tk.Label(stat3, text="0",
                                         bg=COLORES['acento'],
                                         fg=COLORES['texto_claro'],
                                         font=("Segoe UI", 20, "bold"))
        self.label_total_ventas.pack()
        tk.Label(stat3, text="Ventas Total", bg=COLORES['acento'],
                fg=COLORES['texto_claro'], font=("Segoe UI", 12)).pack()
        
        # Estadística 4: Productos con stock bajo
        stat4 = tk.Frame(stats_container, bg=COLORES['peligro'],
                        relief="raised", bd=2, padx=20, pady=15)
        stat4.pack(side=tk.LEFT, padx=20)
        
        tk.Label(stat4, text="⚠️", bg=COLORES['peligro'],
                font=("Segoe UI", 24)).pack()
        self.label_stock_bajo = tk.Label(stat4, text="0",
                                       bg=COLORES['peligro'],
                                       fg=COLORES['texto_claro'],
                                       font=("Segoe UI", 20, "bold"))
        self.label_stock_bajo.pack()
        tk.Label(stat4, text="Stock Bajo", bg=COLORES['peligro'],
                fg=COLORES['texto_claro'], font=("Segoe UI", 12)).pack()
        
        # Estadística 5: Productos próximos a vencer
        stat5 = tk.Frame(stats_container, bg=COLORES['advertencia'],
                        relief="raised", bd=2, padx=20, pady=15)
        stat5.pack(side=tk.LEFT, padx=20)
        
        tk.Label(stat5, text="📅", bg=COLORES['advertencia'],
                font=("Segoe UI", 24)).pack()
        self.label_proximos_vencer = tk.Label(stat5, text="0",
                                            bg=COLORES['advertencia'],
                                            fg=COLORES['texto_claro'],
                                            font=("Segoe UI", 20, "bold"))
        self.label_proximos_vencer.pack()
        tk.Label(stat5, text="Próx. a Vencer", bg=COLORES['advertencia'],
                fg=COLORES['texto_claro'], font=("Segoe UI", 12)).pack()
    
    def crear_historial_ventas(self, padre):
        # Marco historial
        marco_historial = tk.Frame(padre, bg=COLORES['tarjeta'], relief="raised", bd=2)
        marco_historial.pack(fill=tk.BOTH, expand=True, pady=20)
        
        titulo = tk.Label(marco_historial, text="📋 HISTORIAL DE VENTAS",
                         bg=COLORES['tarjeta'], fg=COLORES['primario'],
                         font=("Segoe UI", 16, "bold"))
        titulo.pack(pady=20)
        
        # Lista de ventas
        ventas_frame = tk.Frame(marco_historial, bg=COLORES['tarjeta'])
        ventas_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        self.lista_ventas = ttk.Treeview(ventas_frame,
                                       columns=("Fecha", "Productos", "Total", "Cliente"),
                                       show="headings")
        
        self.lista_ventas.heading("Fecha", text="FECHA Y HORA")
        self.lista_ventas.heading("Productos", text="PRODUCTOS VENDIDOS")
        self.lista_ventas.heading("Total", text="TOTAL VENTA")
        self.lista_ventas.heading("Cliente", text="CLIENTE")
        
        self.lista_ventas.column("Fecha", width=200, anchor=tk.CENTER)
        self.lista_ventas.column("Productos", width=300)
        self.lista_ventas.column("Total", width=150, anchor=tk.CENTER)
        self.lista_ventas.column("Cliente", width=200)
        
        scrollbar_ventas = ttk.Scrollbar(ventas_frame, orient="vertical",
                                       command=self.lista_ventas.yview)
        self.lista_ventas.configure(yscrollcommand=scrollbar_ventas.set)
        
        scrollbar_ventas.pack(side="right", fill="y")
        self.lista_ventas.pack(fill=tk.BOTH, expand=True)
        
        # Botones de reportes
        botones_frame = tk.Frame(marco_historial, bg=COLORES['tarjeta'])
        botones_frame.pack(fill=tk.X, pady=20)
        
        ttk.Button(botones_frame, text="📊 Reporte de Ventas",
                  style="Primario.TButton",
                  command=self.generar_reporte_ventas).pack(side=tk.LEFT, padx=10)
        
        ttk.Button(botones_frame, text="📦 Reporte de Inventario",
                  style="Primario.TButton",
                  command=self.generar_reporte_inventario).pack(side=tk.LEFT, padx=10)
    
    def crear_footer(self):
        footer = tk.Frame(self.ventana, bg=COLORES['fondo_oscuro'], height=40)
        footer.pack(fill=tk.X, side=tk.BOTTOM)
        footer.pack_propagate(False)
        
        info_texto = f"© 2024 Sistema de Gestión Empresarial Avanzado v5.0 | Desarrollado con ❤️ | Usuario: {usuario_actual}"
        tk.Label(footer, text=info_texto,
                bg=COLORES['fondo_oscuro'], fg=COLORES['texto_claro'],
                font=("Segoe UI", 10)).pack(pady=10)
    
    # ============= MÉTODOS DE FUNCIONALIDAD =============
    
    def agregar_producto(self):
        nombre = self.entry_nombre.get().strip()
        try:
            cantidad = int(self.entry_cantidad.get())
            precio = float(self.entry_precio.get())
            minimo = int(self.entry_minimo.get())
        except ValueError:
            messagebox.showerror("❌ Error", "Por favor ingrese valores numéricos válidos para cantidad, precio y stock mínimo.")
            return

        if not nombre:
            messagebox.showwarning("⚠️ Advertencia", "El nombre del producto no puede estar vacío.")
            return
            
        if cantidad < 0 or precio < 0 or minimo < 0:
            messagebox.showwarning("⚠️ Advertencia", "La cantidad, precio y stock mínimo deben ser valores positivos.")
            return
            
        categoria = self.combo_categoria.get()
        proveedor = self.combo_proveedor.get()
        ubicacion = self.entry_ubicacion.get()
        lote = self.entry_lote.get()
        
        # Procesar fecha de vencimiento
        fecha_vencimiento = None
        if self.entry_vencimiento.get():
            try:
                fecha_vencimiento = datetime.strptime(self.entry_vencimiento.get(), "%d/%m/%Y")
            except ValueError:
                messagebox.showerror("❌ Error", "Formato de fecha incorrecto. Use dd/mm/aaaa.")
                return
        
        if nombre in inventario:
            respuesta = messagebox.askyesno("🔄 Confirmación", 
                            f"El producto '{nombre}' ya existe.\n¿Desea actualizar sus datos?")
            if respuesta:
                inventario[nombre] = Producto(
                    nombre, cantidad, precio, categoria, proveedor, minimo,
                    fecha_vencimiento, lote, ubicacion
                )
                self.actualizar_lista()
                self.limpiar_campos()
                messagebox.showinfo("✅ Actualizado", f"Producto '{nombre}' actualizado correctamente.")
        else:
            inventario[nombre] = Producto(
                nombre, cantidad, precio, categoria, proveedor, minimo,
                fecha_vencimiento, lote, ubicacion
            )
            self.actualizar_lista()
            self.limpiar_campos()
            messagebox.showinfo("✅ Éxito", f"Producto '{nombre}' agregado correctamente.")
        
        self.actualizar_estadisticas()
        self.actualizar_alertas()
        self.guardar_datos()

    def eliminar_producto(self):
        seleccionado = self.lista_inventario.selection()
        if seleccionado:
            nombre = self.lista_inventario.item(seleccionado, 'values')[0]
            respuesta = messagebox.askyesno("🗑️ Confirmar eliminación", 
                          f"¿Está seguro de eliminar el producto '{nombre}'?\nEsta acción no se puede deshacer.")
            if respuesta:
                del inventario[nombre]
                self.actualizar_lista()
                self.actualizar_estadisticas()
                self.actualizar_alertas()
                self.guardar_datos()
                messagebox.showinfo("✅ Eliminado", f"Producto '{nombre}' eliminado correctamente.")
        else:
            messagebox.showinfo("ℹ️ Información", "Por favor seleccione un producto de la lista.")

    def modificar_producto(self):
        seleccionado = self.lista_inventario.selection()
        if seleccionado:
            nombre = self.lista_inventario.item(seleccionado, 'values')[0]
            producto = inventario[nombre]
            
            # Crear ventana de edición
            ventana_edicion = tk.Toplevel(self.ventana)
            ventana_edicion.title(f"✏️ Editar {nombre}")
            ventana_edicion.geometry("500x600")
            ventana_edicion.resizable(False, False)
            
            # Marco principal
            marco_edicion = tk.Frame(ventana_edicion, bg=COLORES['fondo'])
            marco_edicion.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
            
            # Campos de edición
            tk.Label(marco_edicion, text="Nombre:", bg=COLORES['fondo'],
                    font=("Segoe UI", 12, "bold")).pack(pady=5)
            entry_nombre_edit = ttk.Entry(marco_edicion, font=("Segoe UI", 12))
            entry_nombre_edit.insert(0, producto.nombre)
            entry_nombre_edit.pack(fill=tk.X, pady=5)
            
            tk.Label(marco_edicion, text="Cantidad:", bg=COLORES['fondo'],
                    font=("Segoe UI", 12, "bold")).pack(pady=5)
            entry_cantidad_edit = ttk.Entry(marco_edicion, font=("Segoe UI", 12))
            entry_cantidad_edit.insert(0, str(producto.cantidad))
            entry_cantidad_edit.pack(fill=tk.X, pady=5)
            
            tk.Label(marco_edicion, text="Precio:", bg=COLORES['fondo'],
                    font=("Segoe UI", 12, "bold")).pack(pady=5)
            entry_precio_edit = ttk.Entry(marco_edicion, font=("Segoe UI", 12))
            entry_precio_edit.insert(0, str(producto.precio))
            entry_precio_edit.pack(fill=tk.X, pady=5)
            
            tk.Label(marco_edicion, text="Categoría:", bg=COLORES['fondo'],
                    font=("Segoe UI", 12, "bold")).pack(pady=5)
            combo_categoria_edit = ttk.Combobox(marco_edicion, 
                                              values=["Electrónica", "Alimentos", "Ropa", "Hogar", "Oficina", "General"],
                                              font=("Segoe UI", 12))
            combo_categoria_edit.set(producto.categoria)
            combo_categoria_edit.pack(fill=tk.X, pady=5)
            
            tk.Label(marco_edicion, text="Proveedor:", bg=COLORES['fondo'],
                    font=("Segoe UI", 12, "bold")).pack(pady=5)
            combo_proveedor_edit = ttk.Combobox(marco_edicion, 
                                              values=list(proveedores.keys()),
                                              font=("Segoe UI", 12))
            combo_proveedor_edit.set(producto.proveedor)
            combo_proveedor_edit.pack(fill=tk.X, pady=5)
            
            tk.Label(marco_edicion, text="Stock mínimo:", bg=COLORES['fondo'],
                    font=("Segoe UI", 12, "bold")).pack(pady=5)
            entry_minimo_edit = ttk.Entry(marco_edicion, font=("Segoe UI", 12))
            entry_minimo_edit.insert(0, str(producto.minimo))
            entry_minimo_edit.pack(fill=tk.X, pady=5)
            
            tk.Label(marco_edicion, text="Fecha Vencimiento (dd/mm/aaaa):", bg=COLORES['fondo'],
                    font=("Segoe UI", 12, "bold")).pack(pady=5)
            entry_vencimiento_edit = ttk.Entry(marco_edicion, font=("Segoe UI", 12))
            if producto.fecha_vencimiento:
                entry_vencimiento_edit.insert(0, producto.fecha_vencimiento.strftime("%d/%m/%Y"))
            entry_vencimiento_edit.pack(fill=tk.X, pady=5)
            
            tk.Label(marco_edicion, text="N° Lote:", bg=COLORES['fondo'],
                    font=("Segoe UI", 12, "bold")).pack(pady=5)
            entry_lote_edit = ttk.Entry(marco_edicion, font=("Segoe UI", 12))
            entry_lote_edit.insert(0, producto.lote if producto.lote else "")
            entry_lote_edit.pack(fill=tk.X, pady=5)
            
            tk.Label(marco_edicion, text="Ubicación:", bg=COLORES['fondo'],
                    font=("Segoe UI", 12, "bold")).pack(pady=5)
            entry_ubicacion_edit = ttk.Entry(marco_edicion, font=("Segoe UI", 12))
            entry_ubicacion_edit.insert(0, producto.ubicacion)
            entry_ubicacion_edit.pack(fill=tk.X, pady=5)
            
            def guardar_cambios():
                try:
                    nuevo_nombre = entry_nombre_edit.get().strip()
                    nueva_cantidad = int(entry_cantidad_edit.get())
                    nuevo_precio = float(entry_precio_edit.get())
                    nueva_categoria = combo_categoria_edit.get()
                    nuevo_proveedor = combo_proveedor_edit.get()
                    nuevo_minimo = int(entry_minimo_edit.get())
                    nueva_ubicacion = entry_ubicacion_edit.get()
                    nuevo_lote = entry_lote_edit.get()
                    
                    # Procesar fecha de vencimiento
                    nueva_fecha_vencimiento = None
                    if entry_vencimiento_edit.get():
                        try:
                            nueva_fecha_vencimiento = datetime.strptime(entry_vencimiento_edit.get(), "%d/%m/%Y")
                        except ValueError:
                            messagebox.showerror("❌ Error", "Formato de fecha incorrecto. Use dd/mm/aaaa.")
                            return
                    
                    if not nuevo_nombre:
                        messagebox.showwarning("⚠️ Advertencia", "El nombre no puede estar vacío.")
                        return
                    
                    # Si cambió el nombre, eliminar el viejo y crear uno nuevo
                    if nuevo_nombre != nombre:
                        del inventario[nombre]
                        inventario[nuevo_nombre] = Producto(
                            nuevo_nombre, nueva_cantidad, nuevo_precio, 
                            nueva_categoria, nuevo_proveedor, nuevo_minimo,
                            nueva_fecha_vencimiento, nuevo_lote, nueva_ubicacion
                        )
                    else:
                        # Actualizar el producto existente
                        producto.cantidad = nueva_cantidad
                        producto.precio = nuevo_precio
                        producto.categoria = nueva_categoria
                        producto.proveedor = nuevo_proveedor
                        producto.minimo = nuevo_minimo
                        producto.fecha_vencimiento = nueva_fecha_vencimiento
                        producto.lote = nuevo_lote
                        producto.ubicacion = nueva_ubicacion
                        producto.fecha_actualizacion = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    
                    self.actualizar_lista()
                    self.actualizar_estadisticas()
                    self.actualizar_alertas()
                    self.guardar_datos()
                    ventana_edicion.destroy()
                    messagebox.showinfo("✅ Éxito", "Producto actualizado correctamente.")
                except ValueError:
                    messagebox.showerror("❌ Error", "Por favor ingrese valores válidos.")
            
            # Botón guardar
            ttk.Button(marco_edicion, text="💾 Guardar Cambios",
                      style="Exito.TButton",
                      command=guardar_cambios).pack(pady=20)
        else:
            messagebox.showinfo("ℹ️ Información", "Por favor seleccione un producto de la lista.")

    def buscar_producto(self):
        nombre = self.entry_nombre.get().strip()
        if not nombre:
            messagebox.showwarning("⚠️ Advertencia", "Ingrese el nombre del producto a buscar.")
            return
            
        if nombre in inventario:
            producto = inventario[nombre]
            valor_total = producto.cantidad * producto.precio
            
            # Información de vencimiento
            info_vencimiento = "No aplica"
            if producto.fecha_vencimiento:
                dias_restantes = (producto.fecha_vencimiento - datetime.now()).days
                if dias_restantes < 0:
                    info_vencimiento = f"VENCIDO (hace {-dias_restantes} días)"
                else:
                    info_vencimiento = f"{producto.fecha_vencimiento.strftime('%d/%m/%Y')} ({dias_restantes} días restantes)"
            
            messagebox.showinfo("🔍 Producto encontrado", 
                f"📦 Producto: {producto.nombre}\n"
                f"📊 Cantidad: {producto.cantidad} unidades\n"
                f"💰 Precio unitario: Bs {producto.precio:.2f}\n"
                f"💵 Valor total: Bs {valor_total:.2f}\n"
                f"🏷️ Categoría: {producto.categoria}\n"
                f"🏭 Proveedor: {producto.proveedor}\n"
                f"⚠️ Stock mínimo: {producto.minimo}\n"
                f"📅 Vencimiento: {info_vencimiento}\n"
                f"🔢 Lote: {producto.lote if producto.lote else 'N/A'}\n"
                f"📍 Ubicación: {producto.ubicacion}\n"
                f"🔄 Última actualización: {producto.fecha_actualizacion}")
        else:
            messagebox.showerror("❌ No encontrado", 
                f"El producto '{nombre}' no existe en el inventario.")

    def actualizar_lista(self):
        # Limpiar la lista
        for item in self.lista_inventario.get_children():
            self.lista_inventario.delete(item)
        
        # Agregar productos ordenados alfabéticamente
        for nombre, producto in sorted(inventario.items(), key=lambda x: x[0]):
            # Determinar alertas
            alerta = ""
            if producto.cantidad < producto.minimo:
                alerta += "⚠️ Stock bajo "
            
            if producto.fecha_vencimiento:
                dias_restantes = (producto.fecha_vencimiento - datetime.now()).days
                if dias_restantes < 0:
                    alerta += "🛑 Vencido"
                elif dias_restantes <= 7:
                    alerta += f"⏳ Vence en {dias_restantes} días"
            
            # Formatear fecha de vencimiento
            fecha_venc = producto.fecha_vencimiento.strftime("%d/%m/%Y") if producto.fecha_vencimiento else "N/A"
            
            # Alternar colores para mejor visualización
            tag = "par" if len(self.lista_inventario.get_children()) % 2 == 0 else "impar"
            
            # Resaltar productos con problemas
            if "🛑" in alerta:
                tag = "vencido"
            elif "⏳" in alerta:
                tag = "por_vencer"
            elif "⚠️" in alerta:
                tag = "stock_bajo"
            
            self.lista_inventario.insert("", "end", values=(
                producto.nombre, 
                producto.cantidad,
                f"Bs {producto.precio:.2f}",
                producto.categoria,
                producto.proveedor,
                producto.minimo,
                fecha_venc,
                producto.lote if producto.lote else "N/A",
                producto.ubicacion,
                alerta.strip() if alerta else "OK"
            ), tags=(tag,))
        
        # Configurar colores alternados y alertas
        self.lista_inventario.tag_configure("par", background="#f8f9fa")
        self.lista_inventario.tag_configure("impar", background="#ffffff")
        self.lista_inventario.tag_configure("stock_bajo", background="#fff3cd")  # Amarillo claro
        self.lista_inventario.tag_configure("por_vencer", background="#ffeeba")  # Amarillo más intenso
        self.lista_inventario.tag_configure("vencido", background="#f8d7da")     # Rojo claro

    def limpiar_campos(self):
        self.entry_nombre.delete(0, tk.END)
        self.entry_cantidad.delete(0, tk.END)
        self.entry_precio.delete(0, tk.END)
        self.combo_categoria.set("General")
        self.combo_proveedor.set("")
        self.entry_minimo.delete(0, tk.END)
        self.entry_minimo.insert(0, "5")
        self.entry_vencimiento.delete(0, tk.END)
        self.entry_lote.delete(0, tk.END)
        self.entry_ubicacion.delete(0, tk.END)
        self.entry_ubicacion.insert(0, "Almacén")
        self.entry_nombre.focus_set()

    def agregar_al_carrito(self):
        seleccionado = self.lista_inventario_ventas.selection()
        if not seleccionado:
            messagebox.showwarning("⚠️ Advertencia", "Seleccione un producto del inventario.")
            return
        
        nombre = self.lista_inventario_ventas.item(seleccionado, 'values')[0]
        producto = inventario[nombre]
        
        if producto.cantidad <= 0:
            messagebox.showwarning("⚠️ Sin stock", f"El producto '{nombre}' no tiene stock disponible.")
            return
        
        # Verificar si el producto está vencido
        if producto.fecha_vencimiento and (producto.fecha_vencimiento - datetime.now()).days < 0:
            respuesta = messagebox.askyesno("🛑 Producto vencido", 
                          f"El producto '{nombre}' está vencido.\n¿Desea venderlo de todas formas?")
            if not respuesta:
                return
        
        # Pedir cantidad a vender
        cantidad = simpledialog.askinteger("🛒 Cantidad a vender", 
                         f"Producto: {nombre}\nDisponible: {producto.cantidad} unidades\n\nIngrese la cantidad a vender:",
                         minvalue=1, maxvalue=producto.cantidad)
        
        if cantidad is None:  # El usuario canceló
            return
        
        if nombre in carrito:
            carrito[nombre]["cantidad"] += cantidad
        else:
            carrito[nombre] = {
                "cantidad": cantidad,
                "precio": producto.precio
            }
        
        # Actualizar inventario temporalmente
        inventario[nombre].cantidad -= cantidad
        
        self.actualizar_carrito()
        self.sincronizar_inventario_ventas()
        messagebox.showinfo("✅ Agregado", f"{cantidad} unidades de '{nombre}' agregadas al carrito.")

    def actualizar_carrito(self):
        global total_venta
        total_venta = 0.0
        
        # Limpiar el carrito
        for item in self.lista_carrito.get_children():
            self.lista_carrito.delete(item)
        
        # Agregar productos al carrito
        for producto, datos in carrito.items():
            subtotal = datos["cantidad"] * datos["precio"]
            total_venta += subtotal
            self.lista_carrito.insert("", "end", values=(
                producto,
                datos["cantidad"],
                f"Bs {datos['precio']:.2f}",
                f"Bs {subtotal:.2f}"
            ))
        
        # Actualizar total
        self.label_total.config(text=f"💵 TOTAL: Bs {total_venta:.2f}")

    def eliminar_del_carrito(self):
        seleccionado = self.lista_carrito.selection()
        if not seleccionado:
            messagebox.showwarning("⚠️ Advertencia", "Seleccione un producto del carrito.")
            return
        
        nombre = self.lista_carrito.item(seleccionado, 'values')[0]
        
        # Devolver la cantidad al inventario
        cantidad_devuelta = carrito[nombre]["cantidad"]
        inventario[nombre].cantidad += cantidad_devuelta
        
        # Eliminar del carrito
        del carrito[nombre]
        
        self.actualizar_carrito()
        self.sincronizar_inventario_ventas()
        messagebox.showinfo("✅ Eliminado", f"Producto '{nombre}' eliminado del carrito.")

    def finalizar_venta(self):
        global total_venta, carrito, ventas
        
        if not carrito:
            messagebox.showwarning("⚠️ Advertencia", "El carrito está vacío.")
            return
        
        # Crear ventana de confirmación
        ventana_confirmacion = tk.Toplevel(self.ventana)
        ventana_confirmacion.title("💳 Confirmar Venta")
        ventana_confirmacion.geometry("600x700")
        ventana_confirmacion.resizable(False, False)
        
        # Información del cliente
        tk.Label(ventana_confirmacion, text="👤 Datos del Cliente", 
                font=("Segoe UI", 14, "bold")).pack(pady=10)
        
        frame_cliente = tk.Frame(ventana_confirmacion)
        frame_cliente.pack(fill=tk.X, padx=20, pady=5)
        
        tk.Label(frame_cliente, text="Nombre:").pack(side=tk.LEFT)
        entry_cliente = ttk.Entry(frame_cliente)
        entry_cliente.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        frame_nit = tk.Frame(ventana_confirmacion)
        frame_nit.pack(fill=tk.X, padx=20, pady=5)
        
        tk.Label(frame_nit, text="NIT/CI:").pack(side=tk.LEFT)
        entry_nit = ttk.Entry(frame_nit)
        entry_nit.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Método de pago
        tk.Label(ventana_confirmacion, text="💳 Método de Pago", 
                font=("Segoe UI", 14, "bold")).pack(pady=10)
        
        metodo_pago = tk.StringVar(value="Efectivo")
        
        frame_pago = tk.Frame(ventana_confirmacion)
        frame_pago.pack(fill=tk.X, padx=20, pady=5)
        
        ttk.Radiobutton(frame_pago, text="💵 Efectivo", variable=metodo_pago, 
                       value="Efectivo").pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(frame_pago, text="💳 Tarjeta", variable=metodo_pago, 
                       value="Tarjeta").pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(frame_pago, text="📲 Transferencia", variable=metodo_pago, 
                       value="Transferencia").pack(side=tk.LEFT, padx=10)
        
        # Resumen de venta
        tk.Label(ventana_confirmacion, text="🧾 Resumen de Venta", 
                font=("Segoe UI", 14, "bold")).pack(pady=10)
        
        frame_resumen = tk.Frame(ventana_confirmacion)
        frame_resumen.pack(fill=tk.X, padx=20, pady=5)
        
        # Encabezados
        tk.Label(frame_resumen, text="Producto", font=("Segoe UI", 10, "bold")).grid(row=0, column=0, sticky=tk.W)
        tk.Label(frame_resumen, text="Cant", font=("Segoe UI", 10, "bold")).grid(row=0, column=1)
        tk.Label(frame_resumen, text="P.Unit", font=("Segoe UI", 10, "bold")).grid(row=0, column=2)
        tk.Label(frame_resumen, text="Subtotal", font=("Segoe UI", 10, "bold")).grid(row=0, column=3)
        
        # Productos
        row = 1
        for producto, datos in carrito.items():
            subtotal = datos["cantidad"] * datos["precio"]
            producto_corto = producto[:15] + "..." if len(producto) > 15 else producto
            
            tk.Label(frame_resumen, text=producto_corto).grid(row=row, column=0, sticky=tk.W)
            tk.Label(frame_resumen, text=str(datos["cantidad"])).grid(row=row, column=1)
            tk.Label(frame_resumen, text=f"{datos['precio']:.2f}").grid(row=row, column=2)
            tk.Label(frame_resumen, text=f"{subtotal:.2f}").grid(row=row, column=3)
            row += 1
        
        # Total
        tk.Label(ventana_confirmacion, text=f"💵 TOTAL: Bs {total_venta:.2f}", 
                font=("Segoe UI", 16, "bold")).pack(pady=10)
        
        def confirmar_y_guardar():
            cliente_nombre = entry_cliente.get().strip() or "Consumidor Final"
            cliente_nit = entry_nit.get().strip() or "0"
            
            # Registrar la venta
            nueva_venta = Venta(carrito.copy(), total_venta, cliente_nombre, metodo_pago.get())
            ventas.append(nueva_venta)
            
            # Registrar cliente si no existe
            if cliente_nit != "0" and cliente_nit not in clientes:
                clientes[cliente_nit] = Cliente(cliente_nombre, cliente_nit)
            
            # Generar ticket
            self.generar_ticket(nueva_venta)
            
            # Limpiar carrito
            carrito.clear()
            self.actualizar_carrito()
            self.sincronizar_inventario_ventas()
            self.actualizar_estadisticas()
            self.actualizar_historial_ventas()
            self.guardar_datos()
            
            ventana_confirmacion.destroy()
            messagebox.showinfo("✅ Venta completada", "La venta se ha registrado correctamente.")
        
        # Botón confirmar
        ttk.Button(ventana_confirmacion, text="✅ Confirmar Venta", 
                  style="Exito.TButton",
                  command=confirmar_y_guardar).pack(pady=20)

    def cancelar_venta(self):
        global carrito
        
        if not carrito:
            return
        
        respuesta = messagebox.askyesno("🚫 Cancelar venta", 
                      "¿Está seguro de cancelar la venta?\nSe devolverán los productos al inventario.")
        
        if respuesta:
            # Devolver todos los productos al inventario
            for producto, datos in carrito.items():
                inventario[producto].cantidad += datos["cantidad"]
            
            carrito.clear()
            self.actualizar_carrito()
            self.sincronizar_inventario_ventas()
            self.limpiar_ticket()
            messagebox.showinfo("🚫 Venta cancelada", "La venta ha sido cancelada correctamente.")

    def generar_ticket(self, venta):
        ticket = "="*50 + "\n"
        ticket += "🏪 SISTEMA DE GESTIÓN EMPRESARIAL\n"
        ticket += "="*50 + "\n"
        ticket += f"📅 Fecha: {venta.fecha}\n"
        ticket += f"👤 Cliente: {venta.cliente}\n"
        ticket += f"💳 Método Pago: {venta.metodo_pago}\n"
        ticket += f"🧾 Ticket de Venta\n"
        ticket += "="*50 + "\n\n"
        
        ticket += f"{'PRODUCTO':<20} {'CANT':<6} {'P.UNIT':<10} {'SUBTOTAL':<10}\n"
        ticket += "-"*50 + "\n"
        
        for producto, datos in venta.productos.items():
            subtotal = datos["cantidad"] * datos["precio"]
            producto_corto = producto[:18] + ".." if len(producto) > 20 else producto
            ticket += f"{producto_corto:<20} {datos['cantidad']:<6} {datos['precio']:<10.2f} {subtotal:<10.2f}\n"
        
        ticket += "-"*50 + "\n"
        ticket += f"{'TOTAL A PAGAR:':<37} Bs {venta.total:>10.2f}\n"
        ticket += "="*50 + "\n"
        ticket += "¡Gracias por su compra!\n"
        ticket += "Vuelva pronto 😊\n"
        ticket += "="*50
        
        # Mostrar ticket
        self.texto_ticket.config(state=tk.NORMAL)
        self.texto_ticket.delete(1.0, tk.END)
        self.texto_ticket.insert(tk.END, ticket)
        self.texto_ticket.config(state=tk.DISABLED)

    def imprimir_ticket(self):
        if not self.texto_ticket.get(1.0, tk.END).strip():
            messagebox.showwarning("⚠️ Advertencia", "No hay ticket para imprimir.")
            return
        
        # Crear un archivo PDF temporal
        temp_pdf = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
        pdf_path = temp_pdf.name
        temp_pdf.close()
        
        try:
            c = canvas.Canvas(pdf_path, pagesize=letter)
            width, height = letter
            
            # Configuración del ticket
            c.setFont("Helvetica", 10)
            line_height = 14
            y_position = height - 50
            
            # Dividir el texto del ticket en líneas
            ticket_text = self.texto_ticket.get(1.0, tk.END)
            lines = ticket_text.split('\n')
            
            # Dibujar cada línea
            for line in lines:
                c.drawString(50, y_position, line)
                y_position -= line_height
                if y_position < 50:  # Nueva página si es necesario
                    c.showPage()
                    y_position = height - 50
                    c.setFont("Helvetica", 10)
            
            c.save()
            
            # Abrir el PDF con el visor predeterminado
            webbrowser.open(pdf_path)
            
        except Exception as e:
            messagebox.showerror("❌ Error", f"No se pudo generar el PDF:\n{str(e)}")
            if os.path.exists(pdf_path):
                os.remove(pdf_path)

    def guardar_ticket(self):
        if not self.texto_ticket.get(1.0, tk.END).strip():
            messagebox.showwarning("⚠️ Advertencia", "No hay ticket para guardar.")
            return
        
        archivo = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")],
            title="Guardar ticket como"
        )
        if archivo:
            try:
                with open(archivo, 'w', encoding='utf-8') as f:
                    f.write(self.texto_ticket.get(1.0, tk.END))
                messagebox.showinfo("✅ Éxito", "Ticket guardado correctamente.")
            except Exception as e:
                messagebox.showerror("❌ Error", f"No se pudo guardar el ticket:\n{str(e)}")

    def limpiar_ticket(self):
        self.texto_ticket.config(state=tk.NORMAL)
        self.texto_ticket.delete(1.0, tk.END)
        self.texto_ticket.config(state=tk.DISABLED)

    def sincronizar_inventario_ventas(self):
        # Limpiar lista
        for item in self.lista_inventario_ventas.get_children():
            self.lista_inventario_ventas.delete(item)
        
        # Agregar productos disponibles
        for nombre, producto in sorted(inventario.items(), key=lambda x: x[0]):
            if producto.cantidad > 0:  # Solo mostrar productos con stock
                # Determinar etiqueta según vencimiento
                tag = "disponible"
                if producto.fecha_vencimiento:
                    dias_restantes = (producto.fecha_vencimiento - datetime.now()).days
                    if dias_restantes < 0:
                        tag = "vencido"
                    elif dias_restantes <= 7:
                        tag = "por_vencer"
                
                fecha_venc = producto.fecha_vencimiento.strftime("%d/%m/%Y") if producto.fecha_vencimiento else "N/A"
                
                self.lista_inventario_ventas.insert("", "end", values=(
                    nombre, 
                    producto.cantidad, 
                    f"Bs {producto.precio:.2f}",
                    fecha_venc
                ), tags=(tag,))
        
        # Configurar colores
        self.lista_inventario_ventas.tag_configure("disponible", background="#d4edda")  # Verde claro
        self.lista_inventario_ventas.tag_configure("por_vencer", background="#ffeeba")  # Amarillo
        self.lista_inventario_ventas.tag_configure("vencido", background="#f8d7da")     # Rojo claro

    def actualizar_estadisticas(self):
        # Total de productos
        total_productos = len(inventario)
        self.label_total_productos.config(text=str(total_productos))
        
        # Ventas del día
        fecha_hoy = datetime.now().strftime("%Y-%m-%d")
        ventas_hoy = sum(venta.total if isinstance(venta, Venta) else venta['total'] for venta in ventas 
                        if (venta.fecha if isinstance(venta, Venta) else venta['fecha']).startswith(fecha_hoy))
        self.label_ventas_dia.config(text=f"Bs {ventas_hoy:.2f}")
        
        # Total de ventas
        total_ventas_count = len(ventas)
        self.label_total_ventas.config(text=str(total_ventas_count))
        
        # Productos con stock bajo
        stock_bajo = sum(1 for producto in inventario.values() if producto.cantidad < producto.minimo)
        self.label_stock_bajo.config(text=str(stock_bajo))
        
        # Productos próximos a vencer (7 días o menos)
        hoy = datetime.now()
        proximos_vencer = sum(1 for producto in inventario.values() 
                             if producto.fecha_vencimiento and 
                             0 <= (producto.fecha_vencimiento - hoy).days <= 7)
        self.label_proximos_vencer.config(text=str(proximos_vencer))

    def actualizar_alertas(self):
        # Limpiar lista de alertas
        for item in self.lista_alertas.get_children():
            self.lista_alertas.delete(item)
        
        # Verificar productos con stock bajo
        for nombre, producto in inventario.items():
            if producto.cantidad < producto.minimo:
                self.lista_alertas.insert("", "end", values=(
                    "⚠️ Stock bajo",
                    nombre,
                    f"Solo quedan {producto.cantidad} unidades (mínimo: {producto.minimo})",
                    "Reponer stock"
                ), tags=("stock_bajo",))
        
        # Verificar productos próximos a vencer (7 días o menos)
        hoy = datetime.now()
        for nombre, producto in inventario.items():
            if producto.fecha_vencimiento:
                dias_restantes = (producto.fecha_vencimiento - hoy).days
                if 0 <= dias_restantes <= 7:
                    self.lista_alertas.insert("", "end", values=(
                        "⏳ Próximo a vencer",
                        nombre,
                        f"Vence en {dias_restantes} días ({producto.fecha_vencimiento.strftime('%d/%m/%Y')})",
                        "Vender o descartar"
                    ), tags=("por_vencer",))
                elif dias_restantes < 0:
                    self.lista_alertas.insert("", "end", values=(
                        "🛑 Vencido",
                        nombre,
                        f"Vencido hace {-dias_restantes} días ({producto.fecha_vencimiento.strftime('%d/%m/%Y')})",
                        "Descartar producto"
                    ), tags=("vencido",))
        
        # Configurar colores para las alertas
        self.lista_alertas.tag_configure("stock_bajo", background="#fff3cd")  # Amarillo claro
        self.lista_alertas.tag_configure("por_vencer", background="#ffeeba")  # Amarillo más intenso
        self.lista_alertas.tag_configure("vencido", background="#f8d7da")     # Rojo claro
        
        # Actualizar estadísticas
        self.actualizar_estadisticas()

    def actualizar_historial_ventas(self):
        # Limpiar lista
        for item in self.lista_ventas.get_children():
            self.lista_ventas.delete(item)
        
        # Agregar ventas (más recientes primero)
        for venta in sorted(ventas, key=lambda x: x.fecha if isinstance(x, Venta) else x['fecha'], reverse=True)[:50]:  # Mostrar últimas 50 ventas
            if isinstance(venta, Venta):
                productos_texto = ", ".join([f"{prod} (x{datos['cantidad']})" for prod, datos in venta.productos.items()])
                total = venta.total
                fecha = venta.fecha
                cliente = venta.cliente
            else:
                productos_texto = ", ".join([f"{prod} (x{datos['cantidad']})" for prod, datos in venta['productos'].items()])
                total = venta['total']
                fecha = venta['fecha']
                cliente = venta.get('cliente', 'Consumidor Final')
            
            self.lista_ventas.insert("", "end", values=(
                fecha,
                productos_texto[:60] + "..." if len(productos_texto) > 60 else productos_texto,
                f"Bs {total:.2f}",
                cliente
            ))

    def exportar_inventario(self):
        archivo = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("Archivos CSV", "*.csv"), ("Todos los archivos", "*.*")],
            title="Guardar inventario como"
        )
        if archivo:
            try:
                with open(archivo, 'w', encoding='utf-8') as f:
                    f.write("Producto,Cantidad,Precio,Categoría,Proveedor,Stock Mínimo,Fecha Vencimiento,Lote,Ubicación,Última Actualización\n")
                    for nombre, producto in inventario.items():
                        fecha_venc = producto.fecha_vencimiento.strftime("%d/%m/%Y") if producto.fecha_vencimiento else ""
                        f.write(f'"{nombre}",{producto.cantidad},{producto.precio},{producto.categoria},'
                                f'"{producto.proveedor}",{producto.minimo},{fecha_venc},'
                                f'"{producto.lote}","{producto.ubicacion}",{producto.fecha_actualizacion}\n')
                messagebox.showinfo("✅ Éxito", "Inventario exportado correctamente.")
            except Exception as e:
                messagebox.showerror("❌ Error", f"No se pudo exportar el inventario:\n{str(e)}")

    def importar_inventario(self):
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
                        
                        # Procesar fecha de vencimiento
                        fecha_vencimiento = None
                        if len(datos) > 6 and datos[6]:
                            try:
                                fecha_vencimiento = datetime.strptime(datos[6], "%d/%m/%Y")
                            except ValueError:
                                pass
                        
                        lote = datos[7].strip('"') if len(datos) > 7 else ""
                        ubicacion = datos[8].strip('"') if len(datos) > 8 else "Almacén"
                        
                        inventario[nombre] = Producto(
                            nombre, cantidad, precio, categoria, proveedor, minimo,
                            fecha_vencimiento, lote, ubicacion
                        )
                
                self.actualizar_lista()
                self.actualizar_estadisticas()
                self.actualizar_alertas()
                self.guardar_datos()
                messagebox.showinfo("✅ Éxito", "Inventario importado correctamente.")
            except Exception as e:
                messagebox.showerror("❌ Error", f"No se pudo importar el inventario:\n{str(e)}")

    def generar_reporte_inventario(self):
        # Crear ventana de opciones de reporte
        ventana_reporte = tk.Toplevel(self.ventana)
        ventana_reporte.title("📊 Generar Reporte de Inventario")
        ventana_reporte.geometry("400x300")
        ventana_reporte.resizable(False, False)
        
        tk.Label(ventana_reporte, text="Opciones de Reporte", font=("Segoe UI", 14, "bold")).pack(pady=10)
        
        # Opciones
        tk.Label(ventana_reporte, text="Tipo de reporte:").pack()
        tipo_reporte = ttk.Combobox(ventana_reporte, values=["Completo", "Solo stock bajo", "Por categoría", "Próximos a vencer"])
        tipo_reporte.pack()
        
        tk.Label(ventana_reporte, text="Formato:").pack()
        formato = ttk.Combobox(ventana_reporte, values=["PDF", "CSV", "Pantalla"])
        formato.pack()
        
        def generar():
            tipo = tipo_reporte.get()
            formato_seleccionado = formato.get()
            
            if not tipo or not formato_seleccionado:
                messagebox.showwarning("⚠️ Advertencia", "Seleccione tipo y formato de reporte.")
                return
            
            # Filtrar productos según el tipo de reporte
            productos_reporte = []
            hoy = datetime.now()
            
            if tipo == "Completo":
                productos_reporte = list(inventario.values())
            elif tipo == "Solo stock bajo":
                productos_reporte = [p for p in inventario.values() if p.cantidad < p.minimo]
            elif tipo == "Por categoría":
                categoria = simpledialog.askstring("Categoría", "Ingrese la categoría a reportar:")
                if categoria:
                    productos_reporte = [p for p in inventario.values() if p.categoria.lower() == categoria.lower()]
                else:
                    return
            elif tipo == "Próximos a vencer":
                dias = simpledialog.askinteger("Días", "Ingrese el número de días para alerta de vencimiento:", minvalue=1)
                if dias:
                    productos_reporte = [p for p in inventario.values() 
                                       if p.fecha_vencimiento and 
                                       0 <= (p.fecha_vencimiento - hoy).days <= dias]
                else:
                    return
            
            if formato_seleccionado == "PDF":
                self.generar_pdf_inventario(productos_reporte, tipo)
            elif formato_seleccionado == "CSV":
                self.generar_csv_inventario(productos_reporte, tipo)
            else:  # Pantalla
                self.mostrar_reporte_pantalla(productos_reporte, tipo)
        
        ttk.Button(ventana_reporte, text="Generar Reporte", command=generar).pack(pady=20)

    def generar_pdf_inventario(self, productos, tipo_reporte):
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
            c.drawString(50, height - 100, f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
            c.drawString(50, height - 120, f"Total productos: {len(productos)}")
            
            # Tabla de productos
            c.setFont("Helvetica-Bold", 10)
            c.drawString(50, height - 150, "Producto")
            c.drawString(200, height - 150, "Cantidad")
            c.drawString(250, height - 150, "Precio")
            c.drawString(300, height - 150, "Categoría")
            c.drawString(400, height - 150, "Proveedor")
            c.drawString(500, height - 150, "Vencimiento")
            
            y_position = height - 170
            c.setFont("Helvetica", 10)
            
            for producto in sorted(productos, key=lambda x: x.nombre):
                if y_position < 100:  # Nueva página si es necesario
                    c.showPage()
                    y_position = height - 50
                    c.setFont("Helvetica", 10)
                
                c.drawString(50, y_position, producto.nombre[:30])
                c.drawString(200, y_position, str(producto.cantidad))
                c.drawString(250, y_position, f"{producto.precio:.2f}")
                c.drawString(300, y_position, producto.categoria)
                c.drawString(400, y_position, producto.proveedor[:15])
                
                fecha_venc = producto.fecha_vencimiento.strftime("%d/%m/%Y") if producto.fecha_vencimiento else "N/A"
                c.drawString(500, y_position, fecha_venc)
                
                y_position -= 20
            
            c.save()
            messagebox.showinfo("✅ Éxito", f"Reporte generado en:\n{archivo}")
            webbrowser.open(archivo)
        except Exception as e:
            messagebox.showerror("❌ Error", f"No se pudo generar el PDF:\n{str(e)}")

    def generar_csv_inventario(self, productos, tipo_reporte):
        archivo = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("Archivos CSV", "*.csv"), ("Todos los archivos", "*.*")],
            title="Guardar reporte como"
        )
        if not archivo:
            return
        
        try:
            with open(archivo, 'w', encoding='utf-8') as f:
                f.write("Producto,Cantidad,Precio,Categoría,Proveedor,Stock Mínimo,Fecha Vencimiento,Lote,Ubicación\n")
                for producto in sorted(productos, key=lambda x: x.nombre):
                    fecha_venc = producto.fecha_vencimiento.strftime("%d/%m/%Y") if producto.fecha_vencimiento else ""
                    f.write(f'"{producto.nombre}",{producto.cantidad},{producto.precio},'
                           f'"{producto.categoria}","{producto.proveedor}",{producto.minimo},'
                           f'"{fecha_venc}","{producto.lote}","{producto.ubicacion}"\n')
            
            messagebox.showinfo("✅ Éxito", f"Reporte generado en:\n{archivo}")
        except Exception as e:
            messagebox.showerror("❌ Error", f"No se pudo generar el CSV:\n{str(e)}")

    def mostrar_reporte_pantalla(self, productos, tipo_reporte):
        ventana_reporte = tk.Toplevel(self.ventana)
        ventana_reporte.title(f"📊 Reporte de Inventario - {tipo_reporte}")
        ventana_reporte.geometry("1000x700")
        
        texto = scrolledtext.ScrolledText(ventana_reporte, width=120, height=30, font=("Courier", 10))
        texto.pack(fill=tk.BOTH, expand=True)
        
        texto.insert(tk.END, f"Reporte de Inventario - {tipo_reporte}\n")
        texto.insert(tk.END, f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n")
        texto.insert(tk.END, f"Total productos: {len(productos)}\n\n")
        
        texto.insert(tk.END, "Producto                     Cantidad   Precio   Categoría       Proveedor          Vencimiento    Lote       Ubicación\n")
        texto.insert(tk.END, "-"*120 + "\n")
        
        for producto in sorted(productos, key=lambda x: x.nombre):
            fecha_venc = producto.fecha_vencimiento.strftime("%d/%m/%Y") if producto.fecha_vencimiento else "N/A"
            texto.insert(tk.END, f"{producto.nombre[:30]:<30} {producto.cantidad:>8} {producto.precio:>8.2f} "
                      f"{producto.categoria[:15]:<15} {producto.proveedor[:15]:<15} {fecha_venc:<15} "
                      f"{producto.lote[:10] if producto.lote else 'N/A':<10} {producto.ubicacion}\n")
        
        texto.config(state=tk.DISABLED)
        
        ttk.Button(ventana_reporte, text="Exportar a PDF", 
                  command=lambda: self.generar_pdf_inventario(productos, tipo_reporte)).pack(pady=5)
        ttk.Button(ventana_reporte, text="Exportar a CSV", 
                  command=lambda: self.generar_csv_inventario(productos, tipo_reporte)).pack(pady=5)

    def generar_reporte_ventas(self):
        ventana_reporte = tk.Toplevel(self.ventana)
        ventana_reporte.title("📊 Generar Reporte de Ventas")
        ventana_reporte.geometry("400x300")
        ventana_reporte.resizable(False, False)
        
        tk.Label(ventana_reporte, text="Opciones de Reporte", font=("Segoe UI", 14, "bold")).pack(pady=10)
        
        # Opciones de fecha
        tk.Label(ventana_reporte, text="Desde (dd/mm/aaaa):").pack()
        entry_desde = ttk.Entry(ventana_reporte)
        entry_desde.pack()
        
        tk.Label(ventana_reporte, text="Hasta (dd/mm/aaaa):").pack()
        entry_hasta = ttk.Entry(ventana_reporte)
        entry_hasta.pack()
        
        tk.Label(ventana_reporte, text="Formato:").pack()
        formato = ttk.Combobox(ventana_reporte, values=["PDF", "CSV", "Pantalla"])
        formato.pack()
        
        def generar():
            fecha_desde = entry_desde.get()
            fecha_hasta = entry_hasta.get()
            formato_seleccionado = formato.get()
            
            if not formato_seleccionado:
                messagebox.showwarning("⚠️ Advertencia", "Seleccione un formato de reporte.")
                return
            
            # Filtrar ventas por fecha si se especificó
            ventas_filtradas = ventas
            if fecha_desde or fecha_hasta:
                try:
                    desde_date = datetime.strptime(fecha_desde, "%d/%m/%Y") if fecha_desde else None
                    hasta_date = datetime.strptime(fecha_hasta, "%d/%m/%Y") if fecha_hasta else None
                    
                    ventas_filtradas = []
                    for venta in ventas:
                        if isinstance(venta, Venta):
                            venta_date = datetime.strptime(venta.fecha.split()[0], "%Y-%m-%d")
                            venta_dict = venta.a_diccionario()
                        else:
                            venta_date = datetime.strptime(venta['fecha'].split()[0], "%Y-%m-%d")
                            venta_dict = venta
                        
                        cumple_desde = True
                        if desde_date:
                            cumple_desde = venta_date >= desde_date
                        
                        cumple_hasta = True
                        if hasta_date:
                            cumple_hasta = venta_date <= hasta_date
                        
                        if cumple_desde and cumple_hasta:
                            ventas_filtradas.append(venta_dict)
                except ValueError:
                    messagebox.showerror("❌ Error", "Formato de fecha incorrecto. Use dd/mm/aaaa.")
                    return
            
            if formato_seleccionado == "PDF":
                self.generar_pdf_ventas(ventas_filtradas, fecha_desde, fecha_hasta)
            elif formato_seleccionado == "CSV":
                self.generar_csv_ventas(ventas_filtradas, fecha_desde, fecha_hasta)
            else:  # Pantalla
                self.mostrar_reporte_ventas_pantalla(ventas_filtradas, fecha_desde, fecha_hasta)
        
        ttk.Button(ventana_reporte, text="Generar Reporte", command=generar).pack(pady=20)

    def generar_pdf_ventas(self, ventas_filtradas, fecha_desde, fecha_hasta):
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
            c.drawString(50, height - 100, f"Fecha de generación: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
            c.drawString(50, height - 120, f"Total ventas: {len(ventas_filtradas)}")
            
            # Resumen
            total_general = sum(v['total'] if isinstance(v, dict) else v.total for v in ventas_filtradas)
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
            
            for venta in sorted(ventas_filtradas, key=lambda x: x['fecha'] if isinstance(x, dict) else x.fecha, reverse=True):
                if y_position < 100:  # Nueva página si es necesario
                    c.showPage()
                    y_position = height - 50
                    c.setFont("Helvetica", 10)
                
                if isinstance(venta, dict):
                    fecha = venta['fecha']
                    cliente = venta.get('cliente', 'Consumidor Final')
                    total = venta['total']
                    metodo_pago = venta.get('metodo_pago', 'Efectivo')
                    vendedor = venta.get('vendedor', 'Desconocido')
                else:
                    fecha = venta.fecha
                    cliente = venta.cliente
                    total = venta.total
                    metodo_pago = venta.metodo_pago
                    vendedor = venta.vendedor
                
                # Formatear fecha para mostrar solo la parte de fecha
                fecha_formateada = fecha.split()[0] if ' ' in fecha else fecha
                
                c.drawString(50, y_position, fecha_formateada)
                c.drawString(150, y_position, cliente[:30])
                c.drawString(300, y_position, f"Bs {total:.2f}")
                c.drawString(400, y_position, metodo_pago)
                c.drawString(500, y_position, vendedor[:15])
                
                y_position -= 20
            
            c.save()
            messagebox.showinfo("✅ Éxito", f"Reporte generado en:\n{archivo}")
            webbrowser.open(archivo)
        except Exception as e:
            messagebox.showerror("❌ Error", f"No se pudo generar el PDF:\n{str(e)}")

    def generar_csv_ventas(self, ventas_filtradas, fecha_desde, fecha_hasta):
        archivo = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("Archivos CSV", "*.csv"), ("Todos los archivos", "*.*")],
            title="Guardar reporte como"
        )
        if not archivo:
            return
        
        try:
            with open(archivo, 'w', encoding='utf-8') as f:
                f.write("Fecha,Cliente,Total,Método Pago,Vendedor,Productos\n")
                for venta in ventas_filtradas:
                    if isinstance(venta, dict):
                        fecha = venta['fecha']
                        cliente = venta.get('cliente', 'Consumidor Final')
                        total = venta['total']
                        metodo_pago = venta.get('metodo_pago', 'Efectivo')
                        vendedor = venta.get('vendedor', 'Desconocido')
                        productos = ", ".join([f"{p} (x{d['cantidad']})" for p, d in venta['productos'].items()])
                    else:
                        fecha = venta.fecha
                        cliente = venta.cliente
                        total = venta.total
                        metodo_pago = venta.metodo_pago
                        vendedor = venta.vendedor
                        productos = ", ".join([f"{p} (x{d['cantidad']})" for p, d in venta.productos.items()])
                    
                    f.write(f'"{fecha}","{cliente}",{total},"{metodo_pago}","{vendedor}","{productos}"\n')
            
            messagebox.showinfo("✅ Éxito", f"Reporte generado en:\n{archivo}")
        except Exception as e:
            messagebox.showerror("❌ Error", f"No se pudo generar el CSV:\n{str(e)}")

    def mostrar_reporte_ventas_pantalla(self, ventas_filtradas, fecha_desde, fecha_hasta):
        ventana_reporte = tk.Toplevel(self.ventana)
        ventana_reporte.title("📊 Reporte de Ventas")
        ventana_reporte.geometry("1000x700")
        
        texto = scrolledtext.ScrolledText(ventana_reporte, width=120, height=30, font=("Courier", 10))
        texto.pack(fill=tk.BOTH, expand=True)
        
        # Encabezado
        texto.insert(tk.END, "REPORTE DE VENTAS\n")
        texto.insert(tk.END, "="*100 + "\n")
        
        rango_fechas = ""
        if fecha_desde and fecha_hasta:
            rango_fechas = f"Del {fecha_desde} al {fecha_hasta}"
        elif fecha_desde:
            rango_fechas = f"Desde {fecha_desde}"
        elif fecha_hasta:
            rango_fechas = f"Hasta {fecha_hasta}"
        
        texto.insert(tk.END, f"{rango_fechas}\n")
        texto.insert(tk.END, f"Fecha de generación: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n")
        texto.insert(tk.END, f"Total ventas: {len(ventas_filtradas)}\n")
        
        # Resumen
        total_general = sum(v['total'] if isinstance(v, dict) else v.total for v in ventas_filtradas)
        texto.insert(tk.END, f"\nTotal general: Bs {total_general:.2f}\n\n")
        
        # Tabla de ventas
        texto.insert(tk.END, "Fecha                Cliente                     Total      Método Pago      Vendedor         Productos\n")
        texto.insert(tk.END, "-"*100 + "\n")
        
        for venta in sorted(ventas_filtradas, key=lambda x: x['fecha'] if isinstance(x, dict) else x.fecha, reverse=True):
            if isinstance(venta, dict):
                fecha = venta['fecha']
                cliente = venta.get('cliente', 'Consumidor Final')
                total = venta['total']
                metodo_pago = venta.get('metodo_pago', 'Efectivo')
                vendedor = venta.get('vendedor', 'Desconocido')
                productos = ", ".join([f"{p} (x{d['cantidad']})" for p, d in venta['productos'].items()])
            else:
                fecha = venta.fecha
                cliente = venta.cliente
                total = venta.total
                metodo_pago = venta.metodo_pago
                vendedor = venta.vendedor
                productos = ", ".join([f"{p} (x{d['cantidad']})" for p, d in venta.productos.items()])
            
            # Formatear fecha para mostrar solo la parte de fecha
            fecha_formateada = fecha.split()[0] if ' ' in fecha else fecha
            
            texto.insert(tk.END, f"{fecha_formateada:<20} {cliente[:25]:<25} Bs {total:>8.2f}  {metodo_pago:<15} {vendedor[:15]:<15} {productos[:30]}\n")
        
        texto.config(state=tk.DISABLED)
        
        # Botones de exportación
        frame_botones = tk.Frame(ventana_reporte)
        frame_botones.pack(pady=10)
        
        ttk.Button(frame_botones, text="Exportar a PDF", 
                  command=lambda: self.generar_pdf_ventas(ventas_filtradas, fecha_desde, fecha_hasta)).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(frame_botones, text="Exportar a CSV", 
                  command=lambda: self.generar_csv_ventas(ventas_filtradas, fecha_desde, fecha_hasta)).pack(side=tk.LEFT, padx=5)

    def on_cambio_pestana(self, event):
        pestana_actual = self.notebook.tab(self.notebook.select(), "text")
        
        if pestana_actual == "📦 INVENTARIO":
            self.actualizar_lista()
        elif pestana_actual == "💳 VENTAS":
            self.sincronizar_inventario_ventas()
        elif pestana_actual == "📊 REPORTES":
            self.actualizar_estadisticas()
            self.actualizar_historial_ventas()
        elif pestana_actual == "🚨 ALERTAS":
            self.actualizar_alertas()

    def iniciar(self):
        # Cargar datos iniciales
        self.actualizar_lista()
        self.sincronizar_inventario_ventas()
        self.actualizar_estadisticas()
        self.actualizar_alertas()
        self.actualizar_historial_ventas()
        
        # Iniciar la aplicación
        self.ventana.mainloop()

# Punto de entrada
if __name__ == "__main__":
    app = InventarioAvanzado()
    app.iniciar()