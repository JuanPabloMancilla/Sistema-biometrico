import customtkinter as ctk
from app.views.user_management_view import UserManagementView
from app.views.account_view import AccountView 
from app.views.facultad_management_view import FacultadManagementView
from app.views.carrera_management_view import CarreraManagementView
from app.views.registro_acceso_management import RegistroAccesoManagementView

# --- VISTA PRINCIPAL DEL DASHBOARD ---
class DashboardView(ctk.CTkFrame):
    def __init__(self, master, on_back):
        super().__init__(master, fg_color="#F8FAFC")
        self.on_back = on_back

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # 1. Sidebar (Fija a la izquierda)
        self.create_sidebar()

        # 2. Panel Derecho (Fijo)
        self.right_panel = ctk.CTkFrame(self, fg_color="transparent")
        self.right_panel.grid(row=0, column=1, sticky="nsew")

        # --- ZONA FIJA: CONTROLES SUPERIORES ---
        # Al crearlos aquí una sola vez, evitamos el parpadeo de segundos
        self.top_ctrl_area = ctk.CTkFrame(self.right_panel, fg_color="transparent")
        self.top_ctrl_area.pack(side="top", fill="x")
        self.create_top_controls(self.top_ctrl_area)

        # --- ZONA VARIABLE: CONTENEDOR DE CONTENIDO ---
        # Este es el único cuadro que se limpiará al cambiar de pestaña
        self.content_container = ctk.CTkFrame(self.right_panel, fg_color="transparent")
        self.content_container.pack(fill="both", expand=True)

        # Cargar vista inicial
        self.mostrar_panel_control()

    def create_top_controls(self, container):
        """Barra de herramientas fija en la esquina superior"""
        controls_wrapper = ctk.CTkFrame(container, fg_color="transparent")
        controls_wrapper.pack(side="right", padx=40, pady=20)

        # Tema
        self.theme_control = ctk.CTkFrame(controls_wrapper, fg_color="#E2E8F0", corner_radius=20, width=110, height=38)
        self.theme_control.pack(side="left", padx=10)
        self.theme_control.pack_propagate(False) 
        
        self.theme_icon = ctk.CTkLabel(self.theme_control, text="☀️", font=("Inter", 16), text_color="black")
        self.theme_icon.place(x=22, y=19, anchor="center") 
        
        self.theme_switch = ctk.CTkSwitch(
            self.theme_control, text="", width=45, progress_color="#1D1D1F",
            button_color="#1D1D1F", command=self.actualizar_icono_tema 
        )
        self.theme_switch.place(x=72, y=19, anchor="center")

        # Idioma
        self.lang_control = ctk.CTkFrame(controls_wrapper, fg_color="#E2E8F0", corner_radius=20, height=38)
        self.lang_control.pack(side="left", padx=10)
        ctk.CTkLabel(self.lang_control, text="🌐", font=("Inter", 16), text_color="black").pack(side="left", padx=(12, 5))
        
        self.es_btn = ctk.CTkButton(self.lang_control, text="ES", width=38, height=28, corner_radius=14, 
                                   fg_color="#1D1D1F", text_color="white", font=("Inter", 11, "bold"),
                                   hover_color="#1D1D1F", command=lambda: self.actualizar_idioma("ES"))
        self.es_btn.pack(side="left", padx=2, pady=5)
        
        self.en_btn = ctk.CTkButton(self.lang_control, text="EN", width=38, height=28, corner_radius=14, 
                                   fg_color="transparent", text_color="#4A4A4A", font=("Inter", 11, "bold"),
                                   hover_color="#CBD5E1", command=lambda: self.actualizar_idioma("EN"))
        self.en_btn.pack(side="left", padx=(2, 10), pady=5)

    def limpiar_derecha(self):
        """Borra solo el contenido variable, respetando los controles superiores"""
        for widget in self.content_container.winfo_children():
            widget.destroy()

    def mostrar_panel_control(self):
        self.limpiar_derecha()
        self.actualizar_navegacion(self.btn_panel)
        
        # El master ahora es self.content_container (debajo de los controles)
        header = ctk.CTkFrame(self.content_container, fg_color="transparent")
        header.pack(fill="x", padx=40, pady=(10, 20))
        ctk.CTkLabel(header, text="Panel de Control", font=("Inter", 28, "bold"), text_color="#1E293B").pack(anchor="w")
        ctk.CTkLabel(header, text="Registro de accesos del sistema", font=("Inter", 16), text_color="#64748B").pack(anchor="w")

        stats_frame = ctk.CTkFrame(self.content_container, fg_color="transparent")
        stats_frame.pack(fill="x", padx=40, pady=10)
        self.create_stat_card(stats_frame, "Total de Registros", "17", "#3B82F6")
        self.create_stat_card(stats_frame, "Accesos Hoy", "0", "#6366F1")
        self.create_stat_card(stats_frame, "Autorizados", "0", "#10B981")
        self.create_stat_card(stats_frame, "Denegados", "0", "#EF4444")

        graph_box = ctk.CTkFrame(self.content_container, fg_color="white", corner_radius=20, border_width=1, border_color="#E2E8F0")
        graph_box.pack(fill="both", expand=True, padx=40, pady=30)
        ctk.CTkLabel(graph_box, text="📈 Tendencia por Hora", font=("Inter", 16, "bold"), text_color="#1E293B").pack(anchor="w", padx=30, pady=20)
        ctk.CTkLabel(graph_box, text="[ Gráfica de Accesos Activa ]", font=("Inter", 18), text_color="#CBD5E1").place(relx=0.5, rely=0.5, anchor="center")

    def mostrar_gestion_usuarios(self):
        self.limpiar_derecha()
        self.actualizar_navegacion(self.btn_users)
        UserManagementView(self.content_container).pack(fill="both", expand=True, padx=40)

    def mostrar_gestion_facultades(self):
        self.limpiar_derecha()
        self.actualizar_navegacion(self.btn_facultades)
        FacultadManagementView(self.content_container).pack(fill="both", expand=True, padx=40)

    def mostrar_gestion_carreras(self):
        self.limpiar_derecha()
        self.actualizar_navegacion(self.btn_carreras)
        CarreraManagementView(self.content_container).pack(fill="both", expand=True, padx=40)

    def mostrar_registro_accesos(self):
        self.limpiar_derecha()
        self.actualizar_navegacion(self.btn_registros)
        RegistroAccesoManagementView(self.content_container).pack(fill="both", expand=True, padx=40)

    def mostrar_cuenta(self):
        self.limpiar_derecha()
        self.actualizar_navegacion(self.btn_account)
        AccountView(self.content_container, on_logout=self.on_back).pack(fill="both", expand=True, padx=40)

    # --- MÉTODOS DE SOPORTE (SIDEBAR Y AUXILIARES) ---
    def actualizar_icono_tema(self):
        if self.theme_switch.get() == 1:
            self.theme_icon.configure(text="🌙")
            self.theme_control.configure(fg_color="#CBD5E1")
        else:
            self.theme_icon.configure(text="☀️")
            self.theme_control.configure(fg_color="#E2E8F0")
        self.theme_icon.place(x=22, y=19, anchor="center")

    def actualizar_idioma(self, lang):
        if lang == "ES":
            self.es_btn.configure(fg_color="#1D1D1F", text_color="white", hover_color="#1D1D1F")
            self.en_btn.configure(fg_color="transparent", text_color="#4A4A4A", hover_color="#CBD5E1")
        else:
            self.en_btn.configure(fg_color="#1D1D1F", text_color="white", hover_color="#1D1D1F")
            self.es_btn.configure(fg_color="transparent", text_color="#4A4A4A", hover_color="#CBD5E1")

    def actualizar_navegacion(self, boton_activo):
        botones = [self.btn_panel, self.btn_users, self.btn_facultades, self.btn_carreras, self.btn_registros, self.btn_account]
        for btn in botones:
            if btn == boton_activo:
                btn.configure(fg_color="#0F172A", text_color="white", hover_color="#000000")
            else:
                btn.configure(fg_color="transparent", text_color="#64748B", hover_color="#F1F5F9")

    def create_stat_card(self, master, title, value, color):
        card = ctk.CTkFrame(master, height=120, fg_color="white", corner_radius=15, border_width=1, border_color="#E2E8F0")
        card.pack(side="left", padx=(0, 20), expand=True, fill="both")
        card.pack_propagate(False)
        ctk.CTkLabel(card, text=title, font=("Inter", 13, "bold"), text_color="#64748B").pack(anchor="w", padx=20, pady=(20, 0))
        ctk.CTkLabel(card, text=value, font=("Inter", 32, "bold"), text_color=color).pack(anchor="w", padx=20)

    def create_sidebar(self):
        sidebar = ctk.CTkFrame(self, width=280, corner_radius=0, fg_color="white", border_width=1, border_color="#E2E8F0")
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_propagate(False)
        
        profile = ctk.CTkFrame(sidebar, fg_color="transparent")
        profile.pack(pady=40, padx=20, fill="x")
        ctk.CTkLabel(profile, text="👤", font=("Arial", 35)).pack(side="left")
        
        text_info = ctk.CTkFrame(profile, fg_color="transparent")
        text_info.pack(side="left", padx=10)
        ctk.CTkLabel(text_info, text="ADMINISTRADOR", font=("Inter", 14, "bold"), text_color="#1E293B").pack(anchor="w")
        ctk.CTkLabel(text_info, text="Control Biométrico", font=("Inter", 11), text_color="#64748B").pack(anchor="w")

        self.btn_panel = ctk.CTkButton(sidebar, text="🏠   Panel de Control", height=45, anchor="w", hover_color="#F1F5F9", command=self.mostrar_panel_control)
        self.btn_panel.pack(pady=5, padx=20, fill="x")

        self.btn_users = ctk.CTkButton(sidebar, text="👥   Gestión de Usuarios", height=45, anchor="w", hover_color="#F1F5F9", command=self.mostrar_gestion_usuarios)
        self.btn_users.pack(pady=5, padx=20, fill="x")

        self.btn_facultades = ctk.CTkButton(sidebar, text="🏛️   Gestión de Facultades", height=45, anchor="w", hover_color="#F1F5F9", command=self.mostrar_gestion_facultades)
        self.btn_facultades.pack(pady=5, padx=20, fill="x")

        self.btn_carreras = ctk.CTkButton(sidebar, text="📚   Gestión de Carreras", height=45, anchor="w", hover_color="#F1F5F9", command=self.mostrar_gestion_carreras)
        self.btn_carreras.pack(pady=5, padx=20, fill="x")

        self.btn_registros = ctk.CTkButton(sidebar,text="🧾   Registro de Accesos", height=45, anchor="w", hover_color="#F1F5F9", command=self.mostrar_registro_accesos)
        self.btn_registros.pack(pady=5, padx=20, fill="x")

        self.btn_account = ctk.CTkButton(sidebar, text="⚙️   Cuenta", height=45, anchor="w", hover_color="#F1F5F9", command=self.mostrar_cuenta)
        self.btn_account.pack(pady=5, padx=20, fill="x")

        ctk.CTkButton(sidebar, text="Volver al Menú", fg_color="transparent", text_color="#EF4444", hover_color="#FEE2E2", font=("Inter", 14, "bold"), command=self.on_back).pack(side="bottom", pady=30, padx=20, fill="x")