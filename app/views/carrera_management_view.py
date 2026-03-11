import customtkinter as ctk
from app.services.carrera_service import (
    obtener_todas_carreras,
    crear_carrera,
    actualizar_carrera,
    eliminar_carrera,
    obtener_carrera_por_id,
    obtener_facultades_para_dropdown
)


class CarreraManagementView(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="#F8FAFC")
        
        self.modo_edicion = False
        self.carrera_actual_id = None
        
        self.crear_vista_tabla()
    
    def crear_vista_tabla(self):
        """Crea la vista principal con tabla de carreras"""
        
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=40, pady=(40, 20))
        
        title_cont = ctk.CTkFrame(header, fg_color="transparent")
        title_cont.pack(side="left")
        ctk.CTkLabel(title_cont, text="Gestión de Carreras", 
                     font=("Inter", 28, "bold"), text_color="#1E293B").pack(anchor="w")
        ctk.CTkLabel(title_cont, text="Administra las carreras del sistema", 
                     font=("Inter", 15), text_color="#64748B").pack(anchor="w")
        
        # Botón Agregar
        self.btn_agregar = ctk.CTkButton(
            header, 
            text="➕ Agregar Carrera", 
            fg_color="#10B981", 
            hover_color="#059669",
            text_color="white",
            font=("Inter", 13, "bold"),
            command=self.abrir_formulario
        )
        self.btn_agregar.pack(side="right", anchor="n")
        
        # Contenedor externo con bordes
        self.tabla_outer = ctk.CTkFrame(self, fg_color="white",
                                        corner_radius=15, border_width=1, 
                                        border_color="#E2E8F0")
        self.tabla_outer.pack(fill="both", expand=True, padx=40, pady=(0, 40))
        
        # Frame scrollable DENTRO del contenedor
        self.tabla_frame = ctk.CTkScrollableFrame(
            self.tabla_outer, 
            fg_color="white",
            scrollbar_button_color="#CBD5E1",
            scrollbar_button_hover_color="#94A3B8"
        )
        self.tabla_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Cargar y mostrar datos
        self.actualizar_tabla()
    
    def actualizar_tabla(self):
        """Obtiene carreras de la BD y las muestra en la tabla"""
        
        # Limpiar tabla anterior
        for widget in self.tabla_frame.winfo_children():
            widget.destroy()
        
        # Obtener carreras de la BD
        carreras = obtener_todas_carreras()
        
        # Crear encabezados
        header_frame = ctk.CTkFrame(self.tabla_frame, fg_color="#F1F5F9")
        header_frame.pack(fill="x", padx=20, pady=(20, 10))
        
        ctk.CTkLabel(header_frame, text="ID", font=("Inter", 12, "bold"), 
                     text_color="#1E293B", width=50).pack(side="left", padx=5)
        ctk.CTkLabel(header_frame, text="Nombre", font=("Inter", 12, "bold"), 
                     text_color="#1E293B").pack(side="left", expand=True, fill="x", padx=5)
        ctk.CTkLabel(header_frame, text="Facultad", font=("Inter", 12, "bold"), 
                     text_color="#1E293B", width=200).pack(side="left", padx=5)
        ctk.CTkLabel(header_frame, text="Estado", font=("Inter", 12, "bold"), 
                     text_color="#1E293B", width=80).pack(side="left", padx=5)
        ctk.CTkLabel(header_frame, text="Acciones", font=("Inter", 12, "bold"), 
                     text_color="#1E293B", width=200).pack(side="left", padx=5)
        
        # Si no hay carreras
        if not carreras:
            ctk.CTkLabel(self.tabla_frame, text="No hay carreras registradas", 
                         font=("Inter", 14), text_color="#94A3B8").pack(pady=40)
            return
        
        # Crear fila para cada carrera
        for carrera in carreras:
            self.crear_fila_carrera(carrera)
    
    def crear_fila_carrera(self, carrera):
        """Crea una fila con los datos de una carrera y botones de acción"""
        
        fila = ctk.CTkFrame(self.tabla_frame, fg_color="white", 
                           border_width=1, border_color="#E2E8F0", 
                           corner_radius=8)
        fila.pack(fill="x", padx=20, pady=5)
        
        # ID
        ctk.CTkLabel(fila, text=str(carrera["id"]), font=("Inter", 12), 
                     text_color="#1E293B", width=50).pack(side="left", padx=5, pady=10)
        
        # Nombre
        ctk.CTkLabel(fila, text=carrera["nombre"], font=("Inter", 12), 
                     text_color="#1E293B").pack(side="left", expand=True, fill="x", padx=5)
        
        # Facultad
        facultad_nombre = carrera["facultad_nombre"] if carrera["facultad_nombre"] else "Sin facultad"
        ctk.CTkLabel(fila, text=facultad_nombre, font=("Inter", 11), 
                     text_color="#64748B", width=200).pack(side="left", padx=5)
        
        # Estado (Badge)
        estado_color = "#10B981" if carrera["estado"] == 1 else "#EF4444"
        estado_texto = "Activa" if carrera["estado"] == 1 else "Inactiva"
        ctk.CTkLabel(fila, text=estado_texto, font=("Inter", 11, "bold"), 
                     text_color=estado_color, width=80).pack(side="left", padx=5)
        
        # Botones de Editar y Eliminar
        btn_editar = ctk.CTkButton(
            fila, text="✏️ Editar", width=90, height=30,
            fg_color="#3B82F6", hover_color="#2563EB",
            font=("Inter", 11, "bold"),
            command=lambda c=carrera: self.abrir_formulario(c["id"])
        )
        btn_editar.pack(side="left", padx=5, pady=10)
        
        btn_eliminar = ctk.CTkButton(
            fila, text="🗑️ Eliminar", width=90, height=30,
            fg_color="#EF4444", hover_color="#DC2626",
            font=("Inter", 11, "bold"),
            command=lambda c=carrera: self.confirmar_eliminar(c["id"], c["nombre"])
        )
        btn_eliminar.pack(side="left", padx=5, pady=10)
    
    def abrir_formulario(self, id_carrera=None):
        """Abre el formulario para crear o editar una carrera"""
        
        # Limpiar vista anterior
        for widget in self.winfo_children():
            widget.destroy()
        
        # Obtener facultades para el dropdown
        facultades_dict = obtener_facultades_para_dropdown()
        facultades_lista = list(facultades_dict.values())
        
        # Preparar datos si es edición
        if id_carrera:
            self.modo_edicion = True
            self.carrera_actual_id = id_carrera
            carrera = obtener_carrera_por_id(id_carrera)
            titulo = "Editar Carrera"
            nombre_actual = carrera["nombre"] if carrera else ""
            facultad_actual_id = carrera["id_facultad"] if carrera else None
            estado_actual = carrera["estado"] if carrera else 1
            facultad_actual_nombre = facultades_dict.get(facultad_actual_id, "Seleccionar facultad")
        else:
            self.modo_edicion = False
            self.carrera_actual_id = None
            titulo = "Crear Nueva Carrera"
            nombre_actual = ""
            facultad_actual_id = None
            estado_actual = 1
            facultad_actual_nombre = "Seleccionar facultad"
        
        # Frame del formulario
        form_frame = ctk.CTkFrame(self, fg_color="#F8FAFC")
        form_frame.pack(fill="both", expand=True)
        
        # Header
        header = ctk.CTkFrame(form_frame, fg_color="transparent")
        header.pack(fill="x", padx=40, pady=(40, 20))
        ctk.CTkLabel(header, text=titulo, font=("Inter", 28, "bold"), 
                     text_color="#1E293B").pack(anchor="w")
        
        # Contenedor del formulario
        form_container = ctk.CTkFrame(form_frame, fg_color="white", 
                                      corner_radius=15, border_width=1, 
                                      border_color="#E2E8F0")
        form_container.pack(fill="x", padx=40, pady=40)
        
        # Campo Nombre
        ctk.CTkLabel(form_container, text="Nombre de la Carrera", 
                     font=("Inter", 13, "bold"), text_color="#1E293B").pack(anchor="w", padx=20, pady=(20, 5))
        
        self.input_nombre = ctk.CTkEntry(
            form_container,
            placeholder_text="Ej: Ingeniería en Sistemas",
            font=("Inter", 13),
            height=40,
            fg_color="#F1F5F9",
            border_color="#E2E8F0"
        )
        self.input_nombre.pack(fill="x", padx=20, pady=(0, 20))
        self.input_nombre.insert(0, nombre_actual)
        
        # Campo Facultad
        ctk.CTkLabel(form_container, text="Facultad", 
                     font=("Inter", 13, "bold"), text_color="#1E293B").pack(anchor="w", padx=20, pady=(0, 5))
        
        self.combo_facultad = ctk.CTkComboBox(
            form_container,
            values=facultades_lista,
            font=("Inter", 13),
            height=40,
            fg_color="#F1F5F9",
            border_color="#E2E8F0"
        )
        self.combo_facultad.pack(fill="x", padx=20, pady=(0, 20))
        self.combo_facultad.set(facultad_actual_nombre)
        
        self.facultades_dict = facultades_dict
        
        # Campo Estado
        ctk.CTkLabel(form_container, text="Estado", 
                     font=("Inter", 13, "bold"), text_color="#1E293B").pack(anchor="w", padx=20, pady=(0, 5))
        
        self.combo_estado = ctk.CTkComboBox(
            form_container,
            values=["Activa", "Inactiva"],
            font=("Inter", 13),
            height=40,
            fg_color="#F1F5F9",
            border_color="#E2E8F0"
        )
        self.combo_estado.pack(fill="x", padx=20, pady=(0, 30))
        self.combo_estado.set("Activa" if estado_actual == 1 else "Inactiva")
        
        # Botones
        btn_frame = ctk.CTkFrame(form_container, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        btn_guardar = ctk.CTkButton(
            btn_frame,
            text="💾 Guardar",
            fg_color="#10B981",
            hover_color="#059669",
            font=("Inter", 13, "bold"),
            height=40,
            command=self.guardar_carrera
        )
        btn_guardar.pack(side="left", padx=5, expand=True, fill="x")
        
        btn_cancelar = ctk.CTkButton(
            btn_frame,
            text="❌ Cancelar",
            fg_color="#6B7280",
            hover_color="#4B5563",
            font=("Inter", 13, "bold"),
            height=40,
            command=self.volver_a_tabla
        )
        btn_cancelar.pack(side="left", padx=5, expand=True, fill="x")
    
    def guardar_carrera(self):
        """Guarda la carrera (crear o editar)"""
        
        nombre = self.input_nombre.get().strip()
        facultad_nombre = self.combo_facultad.get()
        estado = 1 if self.combo_estado.get() == "Activa" else 0
        
        if not nombre:
            print("Error: El nombre no puede estar vacío")
            return
        
        if facultad_nombre == "Seleccionar facultad":
            print("Error: Debes seleccionar una facultad")
            return
        
        id_facultad = None
        for fac_id, fac_nombre in self.facultades_dict.items():
            if fac_nombre == facultad_nombre:
                id_facultad = fac_id
                break
        
        if id_facultad is None:
            print("Error: Facultad no válida")
            return
        
        if self.modo_edicion:
            exito = actualizar_carrera(self.carrera_actual_id, nombre, id_facultad, estado)
            if exito:
                print(f"Carrera actualizada: {nombre}")
            else:
                print("Error al actualizar")
        else:
            exito = crear_carrera(nombre, id_facultad, estado)
            if exito:
                print(f"Carrera creada: {nombre}")
            else:
                print("Error al crear")
        
        self.volver_a_tabla()
    
    def confirmar_eliminar(self, id_carrera, nombre_carrera):
        """Elimina una carrera"""
        
        exito = eliminar_carrera(id_carrera)
        
        if exito:
            print(f"Carrera eliminada: {nombre_carrera}")
            self.actualizar_tabla()
        else:
            print("Error al eliminar")
    
    def volver_a_tabla(self):
        """Vuelve a mostrar la tabla desde el formulario"""
        
        for widget in self.winfo_children():
            widget.destroy()
        
        self.crear_vista_tabla()