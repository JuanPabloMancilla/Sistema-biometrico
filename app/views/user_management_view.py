import customtkinter as ctk
from app.services.carrera_service import obtener_todas_carreras, obtener_facultades_para_dropdown
from app.services.usuario import (
    insertar_usuario, 
    actualizar_usuario,
    obtener_usuarios_formateados, 
    obtener_id_facultad_por_nombre, 
    obtener_id_rol_por_nombre,
    desactivar_usuario 
)

class UserManagementView(ctk.CTkFrame):
    def __init__(self, master, controller=None):
        super().__init__(master, fg_color="#F8FAFC")
        self.controller = controller
        self.usuario_editando_id = None 
        
        # --- Inicialización de variables ---
        self.rol_var = ctk.StringVar(value="ESTUDIANTE")
        self.carrera_var = ctk.StringVar()
        self.inputs_obligatorios = {}
        self.inputs_apellidos = {}
        
        self.refresh_data()

        self.colors = {
            "DOCENTE": {"bg": "#F3E8FF", "text": "#A855F7"}, 
            "ESTUDIANTE": {"bg": "#DBEAFE", "text": "#3B82F6"}, 
            "AUXILIAR": {"bg": "#D1FAE5", "text": "#10B981"}
        }
        
        self.filtro_rol_actual = "Todos"
        self.filter_visible = False 

        self.vista_tabla = ctk.CTkFrame(self, fg_color="transparent")
        self.vista_tabla.pack(fill="both", expand=True)

        self.create_header(self.vista_tabla)
        self.create_search_bar(self.vista_tabla)
        
        # Contenedor para filtros
        self.filter_container = ctk.CTkFrame(self.vista_tabla, fg_color="transparent")
        
        self.main_card = ctk.CTkFrame(self.vista_tabla, fg_color="white", corner_radius=15, border_width=1, border_color="#E2E8F0")
        self.main_card.pack(expand=True, fill="both", padx=30, pady=(5, 15))
        
        self.render_table_content(self.all_users)

    def refresh_data(self):
        try:
            self.all_users = obtener_usuarios_formateados()
        except:
            self.all_users = []

    def validar_numeros(self, P):
        return (str.isdigit(P) and len(P) <= 8) or P == ""

    def abrir_camara_facial(self):
        print("📸 Iniciando captura de huella facial...")

    def abrir_formulario(self, usuario=None):
        self.vista_tabla.pack_forget()
        self.inputs_obligatorios = {}
        self.inputs_apellidos = {}
        self.usuario_editando_id = usuario["c"] if usuario else None 
        
        if usuario: self.rol_var.set(usuario["r"])
        else: self.rol_var.set("ESTUDIANTE")
        
        # Carga de datos para dropdowns
        self.dict_facultades = obtener_facultades_para_dropdown()
        nombres_facultades = list(self.dict_facultades.values())
        todas_carreras = obtener_todas_carreras()
        self.carreras_por_plantel = {}
        for c in todas_carreras:
            fn = c['facultad_nombre']
            if fn not in self.carreras_por_plantel: self.carreras_por_plantel[fn] = []
            self.carreras_por_plantel[fn].append(c['nombre'])

        self.form_base = ctk.CTkFrame(self, fg_color="#F8FAFC")
        self.form_base.pack(fill="both", expand=True)
        self.form_container = ctk.CTkScrollableFrame(self.form_base, fg_color="transparent")
        self.form_container.pack(fill="both", expand=True, padx=10, pady=10)

        titulo = "Editar Registro" if usuario else "Nuevo Registro"
        ctk.CTkLabel(self.form_container, text=titulo, font=("Inter", 28, "bold"), text_color="#000000").pack(anchor="w", padx=60, pady=(30, 10))

        # --- SECCIÓN: CLASIFICACIÓN (TU DISEÑO GRIS) ---
        card_clasi = ctk.CTkFrame(self.form_container, fg_color="white", corner_radius=12, border_width=1, border_color="#E2E8F0")
        card_clasi.pack(fill="x", padx=60, pady=10)
        grid = ctk.CTkFrame(card_clasi, fg_color="transparent"); grid.pack(fill="x", padx=20, pady=20)

        gris_f, gris_b, gris_h = "#F1F5F9", "#E2E8F0", "#CBD5E1"
        
        ctk.CTkOptionMenu(grid, values=["ESTUDIANTE", "DOCENTE", "AUXILIAR"], variable=self.rol_var, height=38, fg_color=gris_f, text_color="#000000", button_color=gris_b, button_hover_color=gris_h).pack(side="left", expand=True, fill="x", padx=5)
        self.plantel_menu = ctk.CTkOptionMenu(grid, values=nombres_facultades if nombres_facultades else ["Sin Datos"], command=self.update_carreras_dinamicas, height=38, fg_color=gris_f, text_color="#000000", button_color=gris_b, button_hover_color=gris_h)
        self.plantel_menu.pack(side="left", expand=True, fill="x", padx=5)
        self.carrera_menu = ctk.CTkOptionMenu(grid, variable=self.carrera_var, values=[], height=38, fg_color=gris_f, text_color="#000000", button_color=gris_b, button_hover_color=gris_h)
        self.carrera_menu.pack(side="left", expand=True, fill="x", padx=5)

        if nombres_facultades: self.update_carreras_dinamicas(nombres_facultades[0])

        # --- BOTÓN BIOMETRÍA ---
        fb = ctk.CTkFrame(self.form_container, fg_color="transparent")
        fb.pack(fill="x", padx=60, pady=10)
        ctk.CTkButton(fb, text="📸 Tomar Huella Facial", font=("Inter", 12, "bold"), fg_color="#4F46E5", hover_color="#4338CA", height=40, command=self.abrir_camara_facial).pack(side="right")

        # --- SECCIONES DE INFORMACIÓN ---
        n_pre = usuario["nombre_solo"] if usuario else ""
        ap_pre = usuario["ap"] if usuario else ""
        am_pre = usuario["am"] if usuario else ""

        self.create_section_card(self.form_container, "👤 Información Personal", [("Nombres", n_pre), ("Apellido Paterno", ap_pre), ("Apellido Materno", am_pre)])
        self.create_section_card(self.form_container, "🆔 Identificación", [("Cuenta", str(usuario["c"]) if usuario else ""), ("Correo", usuario["m"] if usuario else "")])

        if usuario: self.inputs_obligatorios["Cuenta"].configure(state="disabled", fg_color="#E2E8F0")

        # --- BOTONES DE ACCIÓN (TUS COLORES GRADUALES) ---
        btns = ctk.CTkFrame(self.form_container, fg_color="transparent")
        btns.pack(fill="x", padx=60, pady=(20, 50))
        
        ctk.CTkButton(btns, text="Cancelar", fg_color="#FEE2E2", text_color="#000000", hover_color="#F87171", command=self.cerrar_formulario, height=45).pack(side="left", expand=True, fill="x", padx=(0, 10))
        
        txt_btn = "Guardar Cambios" if usuario else "Guardar Registro"
        ctk.CTkButton(btns, text=txt_btn, fg_color="#D1FAE5", text_color="#000000", hover_color="#10B981", height=45, command=self.validar_y_guardar).pack(side="left", expand=True, fill="x", padx=(10, 0))

    def validar_y_guardar(self):
            try:
                # 1. Obtención de datos de los inputs
                n = self.inputs_obligatorios.get("Nombres").get().strip()
                ap = self.inputs_apellidos.get("Apellido Paterno").get().strip()
                am = self.inputs_apellidos.get("Apellido Materno").get().strip()
                em = self.inputs_obligatorios.get("Correo").get().strip()
                
                # Obtener cuenta
                if self.usuario_editando_id:
                    cta = self.usuario_editando_id
                else:
                    cta = self.inputs_obligatorios.get("Cuenta").get().strip()
                
                # Validaciones básicas
                if not n or not cta or not em:
                    print("⚠️ Faltan campos obligatorios")
                    return
                
                # 2. Obtención de IDs de catálogos
                id_rol = obtener_id_rol_por_nombre(self.rol_var.get())
                id_facultad = obtener_id_facultad_por_nombre(self.plantel_menu.get())
                id_carrera = None # Opcional: puedes implementar obtener_id_carrera_por_nombre

                # 3. Llamada al servicio (desempaquetando exito y mensaje)
                if self.usuario_editando_id:
                    exito, msg = actualizar_usuario(cta, n, ap, am, id_rol, id_facultad, em)
                else:
                    exito, msg = insertar_usuario(n, ap, am, id_rol, id_facultad, id_carrera, cta, em)
                
                # 4. Refrescar la UI solo si fue exitoso
                if exito:
                    print(f"✅ {msg}")
                    self.refresh_data() # Esto actualiza self.all_users desde la DB
                    self.render_table_content(self.all_users) # Esto dibuja la tabla nueva
                    self.cerrar_formulario()
                else:
                    print(f"❌ Error al guardar: {msg}")

            except Exception as e:
                print(f"💥 Error crítico en la vista: {e}")

    def render_table_content(self, user_list):
        for w in self.main_card.winfo_children(): w.destroy()
        scroll = ctk.CTkScrollableFrame(self.main_card, fg_color="transparent")
        scroll.pack(expand=True, fill="both")
        for u in user_list:
            row = ctk.CTkFrame(scroll, fg_color="transparent", height=85); row.pack(fill="x", pady=2)
            ctk.CTkLabel(row, text="👤", font=("Inter", 35), width=120).pack(side="left", padx=20)
            inf = ctk.CTkFrame(row, fg_color="transparent"); inf.pack(side="left", expand=True, fill="x", pady=10)
            top_line = ctk.CTkFrame(inf, fg_color="transparent"); top_line.pack(anchor="w")
            
            nombre_completo = f"{u.get('nombre_solo', '')} {u.get('ap', '')} {u.get('am', '')}".strip()
            ctk.CTkLabel(top_line, text=nombre_completo, font=("Inter", 15, "bold"), text_color="#000000").pack(side="left")
            
            col = self.colors.get(u["r"].upper(), {"bg": "#E2E8F0", "text": "#475569"})
            badge = ctk.CTkFrame(top_line, fg_color=col["bg"], corner_radius=6); badge.pack(side="left", padx=10)
            ctk.CTkLabel(badge, text=u["r"], font=("Inter", 10, "bold"), text_color=col["text"]).pack(padx=8, pady=2)
            
            ctk.CTkLabel(inf, text=f"Cuenta: {u['c']}  •  {u['m']}", font=("Inter", 12), text_color="#64748B").pack(anchor="w")
            
            act = ctk.CTkFrame(row, fg_color="transparent"); act.pack(side="right", padx=20)
            ctk.CTkButton(act, text="✏️", width=35, height=35, fg_color="#F1F5F9", hover_color="#E2E8F0", text_color="#000000", command=lambda d=u: self.abrir_formulario(d)).pack(side="left", padx=5)
            ctk.CTkButton(act, text="🗑️", width=35, height=35, fg_color="#FFF1F2", hover_color="#FEE2E2", text_color="#E11D48", command=lambda i=u['c']: self.ejecutar_eliminacion(i)).pack(side="left", padx=5)

    def create_search_bar(self, master):
        bar = ctk.CTkFrame(master, fg_color="transparent"); bar.pack(fill="x", padx=30, pady=10)
        self.entry_busqueda = ctk.CTkEntry(bar, placeholder_text="🔍 Buscar...", height=42, corner_radius=10, fg_color="#F1F5F9", border_color="#E2E8F0", border_width=1, text_color="#000000")
        self.entry_busqueda.pack(side="left", fill="x", expand=True, padx=(0, 15))
        self.btn_filter = ctk.CTkButton(bar, text="Filtrar ⌵", width=110, height=42, corner_radius=10, fg_color="white", hover_color="#F1F5F9", text_color="#000000", border_width=1, border_color="#E2E8F0", command=self.toggle_filter)
        self.btn_filter.pack(side="left")

    def toggle_filter(self):
        if not self.filter_visible:
            self.draw_tags(); self.filter_container.pack(fill="x", padx=30, pady=(0, 15), before=self.main_card)
            self.btn_filter.configure(text="Filtrar ︿"); self.filter_visible = True
        else:
            self.filter_container.pack_forget(); self.btn_filter.configure(text="Filtrar ⌵"); self.filter_visible = False

    def draw_tags(self):
        if not hasattr(self, 'filter_container'): self.filter_container = ctk.CTkFrame(self.vista_tabla, fg_color="transparent")
        for w in self.filter_container.winfo_children(): w.destroy()
        r1 = ctk.CTkFrame(self.filter_container, fg_color="transparent"); r1.pack(fill="x", padx=20, pady=(10, 5))
        ctk.CTkLabel(r1, text="👤 Rol:", font=("Inter", 12, "bold"), text_color="#000000", width=80, anchor="w").pack(side="left")
        for t in ["Todos", "Estudiante", "Docente", "Auxiliar"]:
            act = self.filtro_rol_actual == t
            ctk.CTkButton(r1, text=t, height=28, corner_radius=10, fg_color="#F1F5F9" if act else "white", hover_color="#E2E8F0", text_color="#000000", border_width=1, command=lambda v=t: self.aplicar_filtro_visual(v, "rol")).pack(side="left", padx=3)

    def aplicar_filtro_visual(self, v, t):
        if t == "rol": self.filtro_rol_actual = v
        self.draw_tags()

    def create_section_card(self, master, title, fields):
        card = ctk.CTkFrame(master, fg_color="white", corner_radius=12, border_width=1, border_color="#E2E8F0")
        card.pack(fill="x", padx=60, pady=10)
        ctk.CTkLabel(card, text=title, font=("Inter", 13, "bold"), text_color="#000000").pack(anchor="w", padx=20, pady=(15, 5))
        grid = ctk.CTkFrame(card, fg_color="transparent"); grid.pack(fill="x", padx=20, pady=(0, 20))
        for label, val in fields:
            f = ctk.CTkFrame(grid, fg_color="transparent"); f.pack(side="left", expand=True, fill="x", padx=5)
            ctk.CTkLabel(f, text=label, font=("Inter", 11, "bold"), text_color="#64748B").pack(anchor="w")
            entry = ctk.CTkEntry(f, height=38, fg_color="#F1F5F9", border_width=0, text_color="#000000")
            entry.insert(0, val)
            if label == "Cuenta": entry.configure(validate="key", validatecommand=(self.register(self.validar_numeros), '%P'))
            entry.pack(fill="x", pady=5)
            if "Apellido" in label: self.inputs_apellidos[label] = entry
            else: self.inputs_obligatorios[label] = entry

    def update_carreras_dinamicas(self, fn):
        c = self.carreras_por_plantel.get(fn, ["No hay carreras"])
        self.carrera_menu.configure(values=c)
        self.carrera_var.set(c[0])

    def cerrar_formulario(self):
        if hasattr(self, 'form_base'): self.form_base.destroy()
        self.vista_tabla.pack(fill="both", expand=True)

    def create_header(self, master):
        h = ctk.CTkFrame(master, fg_color="transparent"); h.pack(fill="x", padx=30, pady=(10, 5))
        ctk.CTkLabel(h, text="abababababababab", font=("Inter", 28, "bold"), text_color="#000000").pack(side="left")
        ctk.CTkButton(h, text="+ Agregar Usuario", fg_color="#000000", hover_color="#262626", corner_radius=10, command=self.abrir_formulario).pack(side="right")

    def ejecutar_eliminacion(self, id_cuenta):
        self.overlay = ctk.CTkFrame(self, fg_color="#262626", corner_radius=0); self.overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
        modal = ctk.CTkFrame(self.overlay, fg_color="white", corner_radius=15, width=360, height=220)
        modal.place(relx=0.5, rely=0.5, anchor="center")
        ctk.CTkLabel(modal, text="¿Estás seguro?", font=("Inter", 18, "bold"), text_color="#E11D48").pack(pady=(25, 5))
        ctk.CTkLabel(modal, text=f"Se desactivará la cuenta:\n{id_cuenta}", font=("Inter", 13), text_color="#64748B", justify="center").pack(pady=10)
        btns = ctk.CTkFrame(modal, fg_color="transparent"); btns.pack(fill="x", side="bottom", pady=20, padx=20)
        ctk.CTkButton(btns, text="No, volver", fg_color="#F1F5F9", text_color="#000000", command=self.cerrar_modal, height=38).pack(side="left", expand=True, padx=5)
        ctk.CTkButton(btns, text="Sí, eliminar", fg_color="#E11D48", text_color="white", command=lambda: self.confirmar_proceso_borrado(id_cuenta), height=38).pack(side="left", expand=True, padx=5)

    def cerrar_modal(self):
        if hasattr(self, 'overlay'): self.overlay.destroy()

    def confirmar_proceso_borrado(self, id_cuenta):
        if desactivar_usuario(id_cuenta):
            self.refresh_data()
            self.render_table_content(self.all_users)
        self.cerrar_modal()