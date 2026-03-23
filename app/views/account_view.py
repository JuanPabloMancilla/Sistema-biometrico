import customtkinter as ctk

class AccountView(ctk.CTkFrame):
    def __init__(self, master, on_logout):
        super().__init__(master, fg_color="#F8FAFC")
        self.on_logout = on_logout
        
        # --- Configuración de Fuentes ---
        self.font_header = ("Inter", 30, "bold")
        self.font_sub = ("Inter", 16, "bold")
        self.font_normal = ("Inter", 13)
        self.font_small = ("Inter", 11, "bold")
        
        # Datos simulados
        self.datos = {
            "nombre": "ADMINISTRADOR DEL SISTEMA",
            "correo": "admin@universidad.edu.mx",
            "tel": "5512345678",
            "facultad": "ADMINISTRACIÓN CENTRAL"
        }

        self.crear_vista_lectura()

    def limpiar_pantalla(self):
        for widget in self.winfo_children():
            widget.destroy()

    def crear_vista_lectura(self):
        """Vista de solo lectura del perfil"""
        self.limpiar_pantalla()
        
        # --- HEADER ---
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=40, pady=(40, 20))
        
        title_cont = ctk.CTkFrame(header, fg_color="transparent")
        title_cont.pack(side="left")
        ctk.CTkLabel(title_cont, text="⚙️ Mi Cuenta", font=self.font_header, text_color="#000000").pack(anchor="w")
        ctk.CTkLabel(title_cont, text="Configura tu perfil y preferencias", font=self.font_normal, text_color="#64748B").pack(anchor="w")

        ctk.CTkButton(header, text="📝 Editar Perfil", fg_color="white", text_color="#000000", 
                     border_width=1, border_color="#E2E8F0", hover_color="#F1F5F9", 
                     width=150, height=40, font=self.font_small,
                     command=self.abrir_formulario_edicion).pack(side="right", anchor="n")

        self.container = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.container.pack(expand=True, fill="both", padx=40)

        # 1. Profile Banner
        self.create_profile_banner(is_editing=False)

        # 2. Personalización (Alineado y en Negro)
        self.create_customization_card()

        # 3. Campos de Datos (Lectura)
        ctk.CTkLabel(self.container, text="📋 Detalles de la Cuenta", font=self.font_sub, text_color="#000000").pack(anchor="w", padx=100, pady=(20, 10))
        self.create_read_only_field("Nombre Completo", self.datos["nombre"], "👤")
        self.create_read_only_field("Correo Institucional", self.datos["correo"], "📧")
        self.create_read_only_field("Teléfono", self.datos["tel"], "📞")
        self.create_read_only_field("Dependencia", self.datos["facultad"], "🏛️")

        # Logout
        ctk.CTkButton(self.container, text="🚪 Cerrar Sesión Segura", fg_color="#FFF1F2", text_color="#E11D48", 
                     hover_color="#FEE2E2", height=50, corner_radius=12, font=self.font_sub, 
                     command=self.on_logout).pack(fill="x", pady=(40, 60), padx=100)

    def create_customization_card(self):
        card = ctk.CTkFrame(self.container, fg_color="white", corner_radius=15, border_width=1, border_color="#E2E8F0")
        card.pack(fill="x", pady=10, padx=100)
        ctk.CTkLabel(card, text="🎨 Personalización", font=self.font_sub, text_color="#000000").pack(anchor="w", padx=20, pady=(15, 10))
        
        # Fila Modo Oscuro
        f1 = ctk.CTkFrame(card, fg_color="transparent", height=40)
        f1.pack(fill="x", padx=20, pady=5)
        ctk.CTkLabel(f1, text="🌙 Modo Oscuro", font=self.font_normal, text_color="#000000").pack(side="left")
        ctk.CTkSwitch(f1, text="", progress_color="#1E293B").pack(side="right")

        # Fila Idioma
        f2 = ctk.CTkFrame(card, fg_color="transparent", height=40)
        f2.pack(fill="x", padx=20, pady=(5, 20))
        ctk.CTkLabel(f2, text="🌐 Idioma del Sistema", font=self.font_normal, text_color="#000000").pack(side="left")
        
        lang_group = ctk.CTkFrame(f2, fg_color="#F1F5F9", corner_radius=10)
        lang_group.pack(side="right")
        ctk.CTkButton(lang_group, text="ES", width=40, height=30, fg_color="#1D1D1F", text_color="white", corner_radius=8, font=self.font_small).pack(side="left", padx=2, pady=2)
        ctk.CTkButton(lang_group, text="EN", width=40, height=30, fg_color="transparent", text_color="#000000", corner_radius=8, font=self.font_small, hover_color="#CBD5E1").pack(side="left", padx=2, pady=2)

    def create_read_only_field(self, label, value, icon):
        f = ctk.CTkFrame(self.container, fg_color="white", height=70, corner_radius=12, border_width=1, border_color="#E2E8F0")
        f.pack(fill="x", pady=5, padx=100)
        f.pack_propagate(False)
        ctk.CTkLabel(f, text=icon, font=("Inter", 18)).place(x=20, rely=0.5, anchor="w")
        ctk.CTkLabel(f, text=label, font=("Inter", 10, "bold"), text_color="#64748B").place(x=55, y=12)
        ctk.CTkLabel(f, text=value, font=self.font_sub, text_color="#000000").place(x=55, y=32)

    # --- FORMULARIO DE EDICIÓN ---
    def abrir_formulario_edicion(self):
        self.limpiar_pantalla()
        
        ctk.CTkLabel(self, text="✏️ Editar Mi Información", font=self.font_header, text_color="#000000").pack(anchor="w", padx=60, pady=(40, 20))

        form_scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        form_scroll.pack(expand=True, fill="both", padx=60)

        # Banner en modo edición con botón de foto
        self.container = form_scroll # Temporal para reusar create_profile_banner
        self.create_profile_banner(is_editing=True)

        card = ctk.CTkFrame(form_scroll, fg_color="white", corner_radius=15, border_width=1, border_color="#E2E8F0")
        card.pack(fill="x", pady=10, padx=100)

        self.ent_nombre = self.create_input(card, "👤 Nombre Completo", self.datos["nombre"])
        self.ent_correo = self.create_input(card, "📧 Correo Institucional", self.datos["correo"])
        self.ent_tel = self.create_input(card, "📞 Teléfono de Contacto", self.datos["tel"])
        
        btns = ctk.CTkFrame(form_scroll, fg_color="transparent")
        btns.pack(fill="x", pady=30, padx=100)
        
        ctk.CTkButton(btns, text="❌ Cancelar", font=self.font_sub, fg_color="#FEE2E2", text_color="#000000", height=55, 
                     command=self.crear_vista_lectura).pack(side="left", expand=True, fill="x", padx=(0, 10))
        
        ctk.CTkButton(btns, text="💾 Guardar Cambios", font=self.font_sub, fg_color="#D1FAE5", text_color="#000000", height=55, 
                     command=self.guardar_datos).pack(side="left", expand=True, fill="x", padx=(10, 0))

    def create_input(self, master, label, value):
        ctk.CTkLabel(master, text=label, font=self.font_small, text_color="#000000").pack(anchor="w", padx=25, pady=(20, 5))
        entry = ctk.CTkEntry(master, height=45, font=self.font_normal, fg_color="#F1F5F9", border_width=0, text_color="#000000")
        entry.insert(0, value)
        entry.pack(fill="x", padx=25, pady=(0, 10))
        return entry

    def create_profile_banner(self, is_editing=False):
        card = ctk.CTkFrame(self.container, fg_color="#1E293B", corner_radius=20, height=160)
        card.pack(fill="x", pady=10, padx=100)
        card.pack_propagate(False)

        avatar = ctk.CTkFrame(card, width=90, height=90, corner_radius=45, fg_color="#334155")
        avatar.place(x=40, rely=0.5, anchor="w")
        ctk.CTkLabel(avatar, text="👤", font=("Inter", 40)).place(relx=0.5, rely=0.5, anchor="center")
        
        if is_editing:
            # Botón para actualizar foto (Solo visible al editar)
            ctk.CTkButton(card, text="📸 Actualizar Foto", font=("Inter", 10, "bold"), 
                         fg_color="#38BDF8", text_color="#082736", height=28, width=120,
                         command=lambda: print("Abriendo selector de archivos...")).place(x=150, rely=0.7, anchor="w")
            
            ctk.CTkLabel(card, text="Editando Perfil...", font=("Inter", 18, "bold"), text_color="#FFFFFF").place(x=150, rely=0.4, anchor="w")
        else:
            ctk.CTkLabel(card, text=self.datos["nombre"], font=("Inter", 20, "bold"), text_color="#FFFFFF").place(x=150, rely=0.45, anchor="w")
            ctk.CTkLabel(card, text="SÚPER USUARIO", font=self.font_small, text_color="#38BDF8").place(x=150, rely=0.58, anchor="w")

    def guardar_datos(self):
        self.datos["nombre"] = self.ent_nombre.get()
        self.datos["correo"] = self.ent_correo.get()
        self.datos["tel"] = self.ent_tel.get()
        self.crear_vista_lectura()