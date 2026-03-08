import customtkinter as ctk

class UserManagementView(ctk.CTkFrame):
    def __init__(self, master, controller=None):
        super().__init__(master, fg_color="#F8FAFC")
        self.controller = controller
        
        self.all_users = [
            {"n": "MARÍA ELENA RODRÍGUEZ HERNÁNDEZ", "c": "31702938", "t": "5512345678", "m": "MARIA.RODRIGUEZ@UNIVERSIDAD.EDU.MX", "r": "Docente", "f": "FACIMAR"},
            {"n": "CARLOS ALBERTO MARTÍNEZ GARCÍA", "c": "31702945", "t": "5523456789", "m": "CARLOS.MARTINEZ@UNIVERSIDAD.EDU.MX", "r": "Estudiante", "f": "FIE"},
            {"n": "ANA PATRICIA LÓPEZ SÁNCHEZ", "c": "31702952", "t": "5534567890", "m": "ANA.LOPEZ@UNIVERSIDAD.EDU.MX", "r": "Estudiante", "f": "FCAM"}
        ]
        
        self.colors = {"Docente": {"bg": "#F3E8FF", "text": "#A855F7"}, "Estudiante": {"bg": "#DBEAFE", "text": "#3B82F6"}, "Auxiliar": {"bg": "#D1FAE5", "text": "#10B981"}}
        self.filtro_rol_actual = "Todos"; self.filtro_plantel_actual = "Todos"; self.filter_visible = False 
        self.inputs_obligatorios = {}; self.inputs_apellidos = {}

        self.vista_tabla = ctk.CTkFrame(self, fg_color="transparent")
        self.vista_tabla.pack(fill="both", expand=True)

        self.create_header(self.vista_tabla)
        self.create_search_bar(self.vista_tabla)
        self.filter_container = ctk.CTkFrame(self.vista_tabla, fg_color="white", corner_radius=15, border_width=1, border_color="#E2E8F0")
        self.main_card = ctk.CTkFrame(self.vista_tabla, fg_color="white", corner_radius=15, border_width=1, border_color="#E2E8F0")
        self.main_card.pack(expand=True, fill="both", padx=30, pady=(5, 15))
        self.render_table_content(self.all_users)

    # --- LÓGICA DE MAYÚSCULAS ---
    def force_uppercase(self, var):
        """Transforma el texto a mayúsculas en tiempo real"""
        var.set(var.get().upper())

    # --- FORMULARIO ---
    def abrir_formulario(self, usuario=None):
        self.vista_tabla.pack_forget()
        self.inputs_obligatorios = {}; self.inputs_apellidos = {}
        self.form_container = ctk.CTkFrame(self, fg_color="#F8FAFC")
        self.form_container.pack(fill="both", expand=True)

        self.error_label = ctk.CTkLabel(self.form_container, text="", text_color="#EF4444", font=("Inter", 12, "bold"))
        self.error_label.pack(pady=(10, 0))

        header = ctk.CTkFrame(self.form_container, fg_color="transparent")
        header.pack(fill="x", padx=60, pady=(5, 10))
        ctk.CTkLabel(header, text="Editar Registro" if usuario else "Nuevo Registro", font=("Inter", 22, "bold"), text_color="#000000").pack(side="left")

        # 1. Clasificación (Con Plantel)
        self.create_section_card(self.form_container, "📍 Clasificación Académica", [
            ("Tipo de Persona", ["ESTUDIANTE", "DOCENTE", "AUXILIAR"], usuario["r"] if usuario else "ESTUDIANTE"),
            ("Plantel", ["FACIMAR", "FIE", "FCAM", "TEC. ENFERMERIA"], usuario["f"] if usuario else "FACIMAR")
        ], is_menu=True)

        # 2. Info Personal
        self.create_section_card(self.form_container, "👤 Información Personal", [
            ("Nombres", usuario["n"] if usuario else ""),
            ("Apellido Paterno", ""),
            ("Apellido Materno", "")
        ])

        # 3. Contacto
        self.create_section_card(self.form_container, "🆔 Identificación y Contacto", [
            ("Cuenta", usuario["c"] if usuario else ""),
            ("Correo", usuario["m"] if usuario else ""),
            ("Teléfono", usuario["t"] if usuario else "")
        ])

        # 4. SEGURIDAD BIOMÉTRICA (Restaurada)
        bio_card = ctk.CTkFrame(self.form_container, fg_color="white", corner_radius=12, border_width=1, border_color="#E2E8F0")
        bio_card.pack(fill="x", padx=60, pady=5)
        ctk.CTkLabel(bio_card, text="📸 Seguridad Biométrica", font=("Inter", 13, "bold"), text_color="#000000").pack(anchor="w", padx=20, pady=(10, 0))
        
        txt_bio = "📸 Actualizar huella de rostro" if usuario else "📸 Añadir huella facial"
        ctk.CTkButton(bio_card, text=txt_bio, fg_color="#3B82F6", hover_color="#2563EB", height=32, corner_radius=8, font=("Inter", 12, "bold")).pack(fill="x", padx=20, pady=15)

        # Botones de Acción
        btns = ctk.CTkFrame(self.form_container, fg_color="transparent")
        btns.pack(fill="x", padx=60, pady=(10, 20))
        ctk.CTkButton(btns, text="Cancelar", fg_color="#FEE2E2", text_color="#EF4444", hover_color="#FECACA", height=40, corner_radius=10, font=("Inter", 14, "bold"), command=self.cerrar_formulario).pack(side="left", expand=True, fill="x", padx=(0, 10))
        ctk.CTkButton(btns, text="Actualizar" if usuario else "Finalizar", fg_color="#10B981", hover_color="#0D9488", height=40, corner_radius=10, font=("Inter", 14, "bold"), command=self.validar_y_guardar).pack(side="left", expand=True, fill="x", padx=(10, 0))

    def create_section_card(self, master, title, fields, is_menu=False):
        card = ctk.CTkFrame(master, fg_color="white", corner_radius=12, border_width=1, border_color="#E2E8F0")
        card.pack(fill="x", padx=60, pady=5)
        ctk.CTkLabel(card, text=title, font=("Inter", 13, "bold"), text_color="#000000").pack(anchor="w", padx=20, pady=(10, 5))
        grid = ctk.CTkFrame(card, fg_color="transparent"); grid.pack(fill="x", padx=20, pady=(0, 15))

        for c in fields:
            label_text = c[0]
            f = ctk.CTkFrame(grid, fg_color="transparent"); f.pack(side="left", expand=True, fill="x", padx=4)
            ctk.CTkLabel(f, text=label_text, font=("Inter", 11, "bold"), text_color="#000000").pack(anchor="w")
            
            if is_menu or (isinstance(c[1], list)):
                ctk.CTkOptionMenu(f, values=c[1], variable=ctk.StringVar(value=c[2]), fg_color="#F1F5F9", text_color="#000000", button_color="#E2E8F0", height=32).pack(fill="x", pady=2)
            else:
                var = ctk.StringVar(value=c[1])
                # Excepciones de mayúsculas
                no_caps = ["Cuenta", "Correo", "Contraseña", "Teléfono"]
                if not any(x in label_text for x in no_caps):
                    var.trace_add("write", lambda *args, v=var: self.force_uppercase(v))

                entry = ctk.CTkEntry(f, height=32, fg_color="#F1F5F9", border_width=0, text_color="#000000", textvariable=var)
                entry.pack(fill="x", pady=2)
                
                if "Apellido" in label_text: self.inputs_apellidos[label_text] = entry
                else: self.inputs_obligatorios[label_text] = entry

    # --- FILTROS (CON HOVER GRIS) ---
    def draw_tags(self):
        for w in self.filter_container.winfo_children(): w.destroy()
        r1 = ctk.CTkFrame(self.filter_container, fg_color="transparent"); r1.pack(fill="x", padx=20, pady=(10, 5))
        ctk.CTkLabel(r1, text="👤 Rol:", font=("Inter", 12, "bold"), text_color="#000000", width=80, anchor="w").pack(side="left")
        for t in ["Todos", "Estudiante", "Docente", "Auxiliar"]:
            act = self.filtro_rol_actual == t
            ctk.CTkButton(r1, text=t, height=28, corner_radius=10, 
                          fg_color="#E2E8F0" if act else "white", 
                          text_color="#000000", border_width=1, border_color="#E2E8F0", 
                          hover_color="#E2E8F0", # Hover Gris
                          command=lambda v=t: self.ejecutar_filtro(v, "rol")).pack(side="left", padx=3)
        
        r2 = ctk.CTkFrame(self.filter_container, fg_color="transparent"); r2.pack(fill="x", padx=20, pady=(5, 10))
        ctk.CTkLabel(r2, text="🏫 Plantel:", font=("Inter", 12, "bold"), text_color="#000000", width=80, anchor="w").pack(side="left")
        for p in ["Todos", "FACIMAR", "FIE", "FCAM", "TEC. ENFERMERIA"]:
            act = self.filtro_plantel_actual == p
            ctk.CTkButton(r2, text=p, height=28, corner_radius=10, 
                          fg_color="#E2E8F0" if act else "white", 
                          text_color="#000000", border_width=1, border_color="#E2E8F0", 
                          hover_color="#E2E8F0", # Hover Gris
                          command=lambda v=p: self.ejecutar_filtro(v, "plantel")).pack(side="left", padx=3)

    # --- RESTO DE LÓGICA ---
    def validar_y_guardar(self):
        errores = False
        for entry in self.inputs_obligatorios.values():
            if not entry.get().strip():
                entry.configure(border_width=1, border_color="#EF4444"); errores = True
            else: entry.configure(border_width=0)
        ape_p = self.inputs_apellidos["Apellido Paterno"].get().strip()
        ape_m = self.inputs_apellidos["Apellido Materno"].get().strip()
        if not ape_p and not ape_m:
            self.inputs_apellidos["Apellido Paterno"].configure(border_width=1, border_color="#EF4444")
            self.inputs_apellidos["Apellido Materno"].configure(border_width=1, border_color="#EF4444"); errores = True
        else:
            self.inputs_apellidos["Apellido Paterno"].configure(border_width=0)
            self.inputs_apellidos["Apellido Materno"].configure(border_width=0)
        if not errores: self.cerrar_formulario()
        else: self.error_label.configure(text="⚠️ Complete los campos en rojo (se requiere al menos un apellido)")

    def cerrar_formulario(self):
        if hasattr(self, 'form_container'): self.form_container.destroy()
        self.vista_tabla.pack(fill="both", expand=True)

    def render_table_content(self, user_list):
        for w in self.main_card.winfo_children(): w.destroy()
        head = ctk.CTkFrame(self.main_card, fg_color="#F8FAFC", height=40, corner_radius=15)
        head.pack(fill="x", padx=2, pady=2)
        ctk.CTkLabel(head, text="   FOTOGRAFÍA", font=("Inter", 11, "bold"), text_color="#64748B", width=120, anchor="w").pack(side="left", padx=20)
        ctk.CTkLabel(head, text="INFORMACIÓN PERSONAL", font=("Inter", 11, "bold"), text_color="#64748B", anchor="w").pack(side="left", expand=True, fill="x")
        ctk.CTkLabel(head, text="ACCIONES   ", font=("Inter", 11, "bold"), text_color="#64748B", width=150, anchor="e").pack(side="right", padx=20)
        scroll = ctk.CTkScrollableFrame(self.main_card, fg_color="transparent", corner_radius=0)
        scroll.pack(expand=True, fill="both")
        for u in user_list:
            row = ctk.CTkFrame(scroll, fg_color="transparent", height=85)
            row.pack(fill="x", pady=1)
            ctk.CTkFrame(row, fg_color="#F1F5F9", height=1).pack(side="bottom", fill="x")
            ctk.CTkLabel(row, text="👤", font=("Inter", 30), width=120).pack(side="left", padx=20)
            info = ctk.CTkFrame(row, fg_color="transparent")
            info.pack(side="left", expand=True, fill="x", pady=10)
            name_row = ctk.CTkFrame(info, fg_color="transparent")
            name_row.pack(fill="x", anchor="w")
            ctk.CTkLabel(name_row, text=u["n"], font=("Inter", 15, "bold"), text_color="#000000").pack(side="left")
            c_data = self.colors.get(u["r"], {"bg": "#E2E8F0", "text": "#475569"})
            badge = ctk.CTkFrame(name_row, fg_color=c_data["bg"], corner_radius=6)
            badge.pack(side="left", padx=10)
            ctk.CTkLabel(badge, text=u["r"].upper(), font=("Inter", 10, "bold"), text_color=c_data["text"]).pack(padx=8, pady=2)
            ctk.CTkLabel(info, text=f"Cuenta: {u['c']}  •  Tel: {u['t']}  •  {u['m']}", font=("Inter", 12), text_color="#64748B").pack(anchor="w")
            btns = ctk.CTkFrame(row, fg_color="transparent")
            btns.pack(side="right", padx=20)
            ctk.CTkButton(btns, text="📝", width=35, height=32, fg_color="white", text_color="#000000", border_width=1, border_color="#E2E8F0", hover_color="#F1F5F9", command=lambda d=u: self.abrir_formulario(d)).pack(side="left", padx=2)
            ctk.CTkButton(btns, text="🗑️", width=35, height=32, fg_color="#FEE2E2", text_color="#EF4444", hover_color="#FECACA").pack(side="left", padx=2)

    def create_header(self, master):
        h = ctk.CTkFrame(master, fg_color="transparent"); h.pack(fill="x", padx=30, pady=(5, 5))
        ctk.CTkLabel(h, text="Gestión de Usuarios", font=("Inter", 24, "bold"), text_color="#000000").pack(side="left")
        ctk.CTkButton(h, text="+ Agregar", fg_color="#000000", hover_color="#262626", height=38, corner_radius=8, command=self.abrir_formulario).pack(side="right")

    def create_search_bar(self, master):
        bar = ctk.CTkFrame(master, fg_color="transparent"); bar.pack(fill="x", padx=30, pady=5)
        ctk.CTkEntry(bar, placeholder_text="🔍 Buscar...", height=40, fg_color="white", border_color="#E2E8F0", text_color="#000000").pack(side="left", fill="x", expand=True, padx=(0, 12))
        self.btn_filter = ctk.CTkButton(bar, text="Filtrar ⌵", width=100, height=40, fg_color="white", text_color="#000000", border_width=1, hover_color="#F1F5F9", command=self.toggle_filter)
        self.btn_filter.pack(side="left")

    def toggle_filter(self):
        if not self.filter_visible:
            self.filter_container.pack(fill="x", padx=30, pady=(0, 15), before=self.main_card)
            self.draw_tags(); self.btn_filter.configure(text="Filtrar  ︿", fg_color="#F1F5F9"); self.filter_visible = True
        else:
            self.filter_container.pack_forget(); self.btn_filter.configure(text="Filtrar  ⌵", fg_color="white"); self.filter_visible = False

    def ejecutar_filtro(self, val, tipo):
        if tipo == "rol": self.filtro_rol_actual = val
        else: self.filtro_plantel_actual = val
        fil = self.all_users
        if self.filtro_rol_actual != "Todos": fil = [u for u in fil if u["r"] == self.filtro_rol_actual]
        if self.filtro_plantel_actual != "Todos": fil = [u for u in fil if u["f"] == self.filtro_plantel_actual]
        self.render_table_content(fil); self.draw_tags()