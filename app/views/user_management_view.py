import customtkinter as ctk

class UserManagementView(ctk.CTkFrame):
    def __init__(self, master, controller=None):
        super().__init__(master, fg_color="#F8FAFC")
        self.controller = controller
        
        self.carreras_por_plantel = {
            "FACIMAR": ["Ingeniería Oceánica", "Licenciatura en Sustentabilidad Marina"],
            "FIE": ["Ingeniero Mecánico Electricista", "Ingeniería en Tecnologías Electrónicas", 
                    "Ingeniería en Mecatrónica", "Ingeniería de Software"],
            "FCAM": ["Contador Público", "Licenciatura en Administración", "Licenciatura en Negocios Digitales"],
            "TEC. ENFERMERIA": ["TEC. ENFERMERIA"]
        }
        
        self.all_users = [
            {"n": "NAOMY MARIA MARTINEZ AGUILAR", "c": "20214875", "m": "nmartinez20@ucol.mx", "r": "ESTUDIANTE", "f": "FIE"},
            {"n": "MARCO ANTONIO SOLIS", "c": "10293847", "m": "msolis@universidad.edu.mx", "r": "DOCENTE", "f": "FACIMAR"}
        ]

        self.colors = {
            "DOCENTE": {"bg": "#F3E8FF", "text": "#A855F7"}, 
            "ESTUDIANTE": {"bg": "#DBEAFE", "text": "#3B82F6"}, 
            "AUXILIAR": {"bg": "#D1FAE5", "text": "#10B981"}
        }
        
        self.filtro_rol_actual = "Todos"
        self.filtro_plantel_actual = "Todos"
        self.filter_visible = False 

        # UI Principal
        self.vista_tabla = ctk.CTkFrame(self, fg_color="transparent")
        self.vista_tabla.pack(fill="both", expand=True)

        self.create_header(self.vista_tabla)
        self.create_search_bar(self.vista_tabla)
        
        self.filter_container = ctk.CTkFrame(self.vista_tabla, fg_color="white", corner_radius=15, border_width=1, border_color="#E2E8F0")
        self.main_card = ctk.CTkFrame(self.vista_tabla, fg_color="white", corner_radius=15, border_width=1, border_color="#E2E8F0")
        self.main_card.pack(expand=True, fill="both", padx=30, pady=(5, 15))
        
        self.render_table_content(self.all_users)

    def abrir_formulario(self, usuario=None):
        """Abre el formulario con una gestión de scroll mejorada para evitar bugs visuales"""
        self.vista_tabla.pack_forget()
        
        # SOLUCIÓN AL BUG: Frame base que ocupa todo el espacio
        self.form_base = ctk.CTkFrame(self, fg_color="#F8FAFC")
        self.form_base.pack(fill="both", expand=True)

        # ScrollableFrame dentro del frame base
        self.form_container = ctk.CTkScrollableFrame(self.form_base, fg_color="transparent", corner_radius=0)
        self.form_container.pack(fill="both", expand=True, padx=10, pady=10)

        # Header
        header_frame = ctk.CTkFrame(self.form_container, fg_color="transparent")
        header_frame.pack(fill="x", padx=60, pady=(30, 10))
        ctk.CTkLabel(header_frame, text="Editar Registro" if usuario else "Nuevo Registro", 
                     font=("Inter", 28, "bold"), text_color="#000000").pack(side="left")

        # 1. Clasificación Académica
        card_clasi = ctk.CTkFrame(self.form_container, fg_color="white", corner_radius=12, border_width=1, border_color="#E2E8F0")
        card_clasi.pack(fill="x", padx=60, pady=10)
        ctk.CTkLabel(card_clasi, text="📍 Clasificación Académica", font=("Inter", 13, "bold"), text_color="#000000").pack(anchor="w", padx=20, pady=(15, 5))
        
        grid_clasi = ctk.CTkFrame(card_clasi, fg_color="transparent")
        grid_clasi.pack(fill="x", padx=20, pady=(0, 20))

        self.crear_input_menu(grid_clasi, "Tipo de Persona", ["ESTUDIANTE", "DOCENTE", "AUXILIAR"], usuario["r"] if usuario else "ESTUDIANTE")
        
        f_plan = ctk.CTkFrame(grid_clasi, fg_color="transparent")
        f_plan.pack(side="left", expand=True, fill="x", padx=5)
        ctk.CTkLabel(f_plan, text="Plantel", font=("Inter", 11, "bold"), text_color="#64748B").pack(anchor="w")
        self.plantel_menu = ctk.CTkOptionMenu(f_plan, values=list(self.carreras_por_plantel.keys()), command=self.update_carreras, 
                                              fg_color="#F1F5F9", text_color="#000000", button_color="#E2E8F0", height=38)
        self.plantel_menu.set(usuario["f"] if usuario else "FACIMAR")
        self.plantel_menu.pack(fill="x", pady=5)

        f_carr = ctk.CTkFrame(grid_clasi, fg_color="transparent")
        f_carr.pack(side="left", expand=True, fill="x", padx=5)
        ctk.CTkLabel(f_carr, text="Carrera", font=("Inter", 11, "bold"), text_color="#64748B").pack(anchor="w")
        self.carrera_var = ctk.StringVar()
        self.carrera_menu = ctk.CTkOptionMenu(f_carr, variable=self.carrera_var, values=[], 
                                              fg_color="#F1F5F9", text_color="#000000", button_color="#E2E8F0", height=38)
        self.carrera_menu.pack(fill="x", pady=5)
        self.update_carreras(self.plantel_menu.get())

        # 2. Información Personal
        self.create_section_card(self.form_container, "👤 Información Personal", 
                                 [("Nombres", usuario["n"] if usuario else ""), ("Apellido Paterno", ""), ("Apellido Materno", "")])

        # 3. Identificación
        self.create_section_card(self.form_container, "🆔 Identificación", 
                                 [("Cuenta", usuario["c"] if usuario else ""), ("Correo", usuario["m"] if usuario else "")])

        # 4. Biometría
        card_bio = ctk.CTkFrame(self.form_container, fg_color="white", corner_radius=12, border_width=1, border_color="#E2E8F0")
        card_bio.pack(fill="x", padx=60, pady=10)
        ctk.CTkLabel(card_bio, text="📸 Seguridad Biométrica", font=("Inter", 13, "bold"), text_color="#000000").pack(anchor="w", padx=20, pady=(15, 5))
        ctk.CTkButton(card_bio, text="Detectar huellas faciales", fg_color="#3B82F6", hover_color="#2563EB", 
                      height=45, font=("Inter", 14, "bold"), corner_radius=8).pack(fill="x", padx=20, pady=(5, 20))

        # Botones de Acción
        btns_frame = ctk.CTkFrame(self.form_container, fg_color="transparent")
        btns_frame.pack(fill="x", padx=60, pady=(20, 50))
        ctk.CTkButton(btns_frame, text="Cancelar", fg_color="#FEE2E2", text_color="#EF4444", hover_color="#FECACA", 
                      height=45, corner_radius=10, command=self.cerrar_formulario).pack(side="left", expand=True, fill="x", padx=(0, 10))
        ctk.CTkButton(btns_frame, text="Guardar Registro", fg_color="#10B981", hover_color="#0D9488", 
                      height=45, corner_radius=10, command=self.cerrar_formulario).pack(side="left", expand=True, fill="x", padx=(10, 0))

    def cerrar_formulario(self):
        """Elimina el frame base del formulario y regresa a la tabla"""
        if hasattr(self, 'form_base'):
            self.form_base.destroy()
        self.vista_tabla.pack(fill="both", expand=True)

    def draw_tags(self):
        for w in self.filter_container.winfo_children(): w.destroy()
        for i, (titulo, opciones, filtro_actual, tipo) in enumerate([
            ("👤 Rol:", ["Todos", "Estudiante", "Docente", "Auxiliar"], self.filtro_rol_actual, "rol"),
            ("🏫 Plantel:", ["Todos", "FACIMAR", "FIE", "FCAM", "TEC. ENFERMERIA"], self.filtro_plantel_actual, "plantel")
        ]):
            row = ctk.CTkFrame(self.filter_container, fg_color="transparent")
            row.pack(fill="x", padx=20, pady=(10 if i==0 else 5, 5 if i==0 else 10))
            ctk.CTkLabel(row, text=titulo, font=("Inter", 12, "bold"), text_color="#000000", width=80, anchor="w").pack(side="left")
            for opt in opciones:
                is_active = filtro_actual == opt
                ctk.CTkButton(row, text=opt, height=28, corner_radius=10, 
                              fg_color="#F1F5F9" if is_active else "white", 
                              text_color="#000000", border_width=1, border_color="#E2E8F0",
                              hover_color="#E2E8F0",
                              command=lambda v=opt, t=tipo: self.aplicar_filtro_visual(v, t)).pack(side="left", padx=3)

    def render_table_content(self, user_list):
        for w in self.main_card.winfo_children(): w.destroy()
        head = ctk.CTkFrame(self.main_card, fg_color="#F8FAFC", height=40, corner_radius=15)
        head.pack(fill="x", padx=2, pady=2)
        ctk.CTkLabel(head, text="    FOTOGRAFÍA", font=("Inter", 11, "bold"), text_color="#64748B", width=120, anchor="w").pack(side="left", padx=20)
        ctk.CTkLabel(head, text="INFORMACIÓN PERSONAL", font=("Inter", 11, "bold"), text_color="#64748B", anchor="w").pack(side="left", expand=True, fill="x")
        
        scroll_table = ctk.CTkScrollableFrame(self.main_card, fg_color="transparent")
        scroll_table.pack(expand=True, fill="both")
        
        for u in user_list:
            row = ctk.CTkFrame(scroll_table, fg_color="transparent", height=85)
            row.pack(fill="x", pady=2)
            ctk.CTkLabel(row, text="👤", font=("Inter", 35), width=120).pack(side="left", padx=20)
            info_frame = ctk.CTkFrame(row, fg_color="transparent")
            info_frame.pack(side="left", expand=True, fill="x", pady=10)
            ctk.CTkLabel(info_frame, text=u["n"], font=("Inter", 15, "bold"), text_color="#000000").pack(anchor="w")
            details = ctk.CTkFrame(info_frame, fg_color="transparent")
            details.pack(anchor="w")
            c = self.colors.get(u["r"].upper(), {"bg": "#E2E8F0", "text": "#475569"})
            badge = ctk.CTkFrame(details, fg_color=c["bg"], corner_radius=6)
            badge.pack(side="left")
            ctk.CTkLabel(badge, text=u["r"], font=("Inter", 10, "bold"), text_color=c["text"]).pack(padx=8, pady=2)
            ctk.CTkLabel(details, text=f"  •  Cuenta: {u['c']}  •  {u['m']}", font=("Inter", 12), text_color="#64748B").pack(side="left")
            btns = ctk.CTkFrame(row, fg_color="transparent")
            btns.pack(side="right", padx=20)
            ctk.CTkButton(btns, text="📝", width=35, height=32, fg_color="white", border_width=1, border_color="#E2E8F0", 
                          hover_color="#F1F5F9", text_color="black", command=lambda d=u: self.abrir_formulario(d)).pack(side="left", padx=2)
            ctk.CTkButton(btns, text="🗑️", width=35, height=32, fg_color="#FEE2E2", text_color="#EF4444", hover_color="#FECACA").pack(side="left", padx=2)

    def update_carreras(self, p):
        self.carrera_menu.configure(values=self.carreras_por_plantel.get(p, []))
        self.carrera_var.set(self.carreras_por_plantel[p][0])

    def aplicar_filtro_visual(self, v, t):
        if t == "rol": self.filtro_rol_actual = v
        else: self.filtro_plantel_actual = v
        self.draw_tags()

    def toggle_filter(self):
        if not self.filter_visible:
            self.draw_tags()
            self.filter_container.pack(fill="x", padx=30, pady=(0, 15), before=self.main_card)
            self.btn_filter.configure(text="Filtrar  ︿", fg_color="#F1F5F9")
            self.filter_visible = True
        else:
            self.filter_container.pack_forget()
            self.btn_filter.configure(text="Filtrar  ⌵", fg_color="white")
            self.filter_visible = False

    def create_section_card(self, master, title, fields):
        card = ctk.CTkFrame(master, fg_color="white", corner_radius=12, border_width=1, border_color="#E2E8F0")
        card.pack(fill="x", padx=60, pady=10)
        ctk.CTkLabel(card, text=title, font=("Inter", 13, "bold"), text_color="#000000").pack(anchor="w", padx=20, pady=(15, 5))
        grid = ctk.CTkFrame(card, fg_color="transparent")
        grid.pack(fill="x", padx=20, pady=(0, 20))
        for label, val in fields:
            f = ctk.CTkFrame(grid, fg_color="transparent"); f.pack(side="left", expand=True, fill="x", padx=5)
            ctk.CTkLabel(f, text=label, font=("Inter", 11, "bold"), text_color="#64748B").pack(anchor="w")
            ctk.CTkEntry(f, height=38, fg_color="#F1F5F9", border_width=0, text_color="#000000", placeholder_text=val).pack(fill="x", pady=5)

    def crear_input_menu(self, master, label, ops, init):
        f = ctk.CTkFrame(master, fg_color="transparent"); f.pack(side="left", expand=True, fill="x", padx=5)
        ctk.CTkLabel(f, text=label, font=("Inter", 11, "bold"), text_color="#64748B").pack(anchor="w")
        m = ctk.CTkOptionMenu(f, values=ops, fg_color="#F1F5F9", text_color="#000000", button_color="#E2E8F0", height=38)
        m.set(init); m.pack(fill="x", pady=5)

    def create_header(self, master):
        h = ctk.CTkFrame(master, fg_color="transparent"); h.pack(fill="x", padx=30, pady=(10, 5))
        ctk.CTkLabel(h, text="Gestión de Usuarios", font=("Inter", 28, "bold"), text_color="#000000").pack(side="left")
        ctk.CTkButton(h, text="+ Agregar Usuario", fg_color="#000000", hover_color="#262626", 
                      height=40, corner_radius=10, font=("Inter", 13, "bold"), command=self.abrir_formulario).pack(side="right")

    def create_search_bar(self, master):
        bar = ctk.CTkFrame(master, fg_color="transparent"); bar.pack(fill="x", padx=30, pady=10)
        ctk.CTkEntry(bar, placeholder_text="🔍 Buscar por nombre o cuenta...", height=42, corner_radius=10, 
                     fg_color="white", border_color="#E2E8F0", text_color="#000000").pack(side="left", fill="x", expand=True, padx=(0, 15))
        self.btn_filter = ctk.CTkButton(bar, text="Filtrar ⌵", width=110, height=42, corner_radius=10, 
                                        fg_color="white", text_color="#000000", border_width=1, border_color="#E2E8F0", 
                                        hover_color="#F1F5F9", command=self.toggle_filter)
        self.btn_filter.pack(side="left")