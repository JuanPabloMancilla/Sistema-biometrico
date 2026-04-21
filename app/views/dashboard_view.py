import customtkinter as ctk
from matplotlib.figure import Figure
from matplotlib.ticker import MaxNLocator
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from app.views.user_management_view import UserManagementView
from app.views.account_view import AccountView 
from app.views.facultad_management_view import FacultadManagementView
from app.views.carrera_management_view import CarreraManagementView

from app.services.theme import COLORS

from datetime import datetime
from tkcalendar import DateEntry
from app.detection.detector_rostro import logs_accesos


class DashboardView(ctk.CTkFrame):
    def __init__(self, master, on_back):
        # Fondo general en gris muy claro
        super().__init__(master, fg_color=COLORS["bg"])
        self.on_back = on_back

        # Configuración de pesos de la cuadrícula
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # 1. Sidebar (Lateral izquierda fija)
        self.create_sidebar()

        # 2. Panel Derecho (Contenedor principal)
        self.right_panel = ctk.CTkFrame(self, fg_color="transparent")
        self.right_panel.grid(row=0, column=1, sticky="nsew")

        # Zona superior de controles (Idioma y Tema) - Fondo Transparente para no chocar
        self.top_ctrl_area = ctk.CTkFrame(self.right_panel, fg_color="transparent", height=70)
        self.top_ctrl_area.pack(side="top", fill="x")
        self.top_ctrl_area.pack_propagate(False)
        self.create_top_controls(self.top_ctrl_area)

        # Contenedor para las vistas dinámicas
        self.content_container = ctk.CTkFrame(self.right_panel, fg_color="transparent")
        self.content_container.pack(fill="both", expand=True)

        # Cargar vista inicial
        self.mostrar_panel_control()

    def toggle_theme(self):
        if self.theme_switch.get() == 1:
            ctk.set_appearance_mode("dark")
        else:
            ctk.set_appearance_mode("light")

    def limpiar_derecha(self):
        """Elimina los widgets de la derecha para cargar una nueva vista"""
        for widget in self.content_container.winfo_children():
            widget.destroy()

    def actualizar_navegacion(self, btn_act):
        """Marca el botón seleccionado con colores oscuros para resaltar sobre el blanco"""
        btns = [self.btn_panel, self.btn_users, self.btn_facultades, self.btn_carreras, self.btn_account]
        for b in btns:
            if b == btn_act:
                # Botón Seleccionado: Azul muy oscuro con texto blanco
                b.configure(fg_color=COLORS["selected"], text_color=("white", "black"), hover_color=COLORS["selected"])
            else:
                # Botones Inactivos: Transparentes con texto negro
                b.configure(fg_color="transparent", text_color=COLORS["text"], hover_color="#F1F5F9")

    # --- MÉTODOS DE NAVEGACIÓN ---
    def mostrar_panel_control(self):
        self.limpiar_derecha()
        self.actualizar_navegacion(self.btn_panel)
        self.render_dashboard_principal()

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

    def mostrar_cuenta(self):
        self.limpiar_derecha()
        self.actualizar_navegacion(self.btn_account)
        AccountView(self.content_container, on_logout=self.on_back).pack(fill="both", expand=True, padx=40)

    # --- RENDERIZADO DEL PANEL DE CONTROL (DASHBOARD) ---
    def render_dashboard_principal(self):
        main_scroll = ctk.CTkScrollableFrame(self.content_container, fg_color="transparent")
        main_scroll.pack(fill="both", expand=True)

        # Header del Dashboard
        header = ctk.CTkFrame(main_scroll, fg_color="transparent")
        header.pack(fill="x", padx=40, pady=(10, 20))
        ctk.CTkLabel(header, text="🏠 Panel de Control", font=("Inter", 28, "bold"), text_color=COLORS["text"]).pack(anchor="w")
        ctk.CTkLabel(header, text="Resumen general y actividad reciente", font=("Inter", 16), text_color=COLORS["subtext"]).pack(anchor="w")

        # Tarjetas de Estadísticas (Stats)
        stats_frame = ctk.CTkFrame(main_scroll, fg_color="transparent")
        stats_frame.pack(fill="x", padx=40, pady=10)
        self.create_stat_card(stats_frame, "👥 Total Registros", "17", "#3B82F6")
        self.create_stat_card(stats_frame, "🕒 Accesos Hoy", "5", "#6366F1")
        self.create_stat_card(stats_frame, "✅ Autorizados", "4", "#10B981")
        self.create_stat_card(stats_frame, "🚫 Denegados", "1", "#EF4444")

        # Contenedor de la Gráfica
        graph_box = ctk.CTkFrame(main_scroll, fg_color=COLORS["card"], corner_radius=20, border_width=1, border_color=COLORS["border"], height=280)
        graph_box.pack(fill="x", padx=40, pady=20)
        graph_box.pack_propagate(False)

        ctk.CTkLabel(graph_box, text="📈 Tendencia de Accesos por Hora", font=("Inter", 16, "bold"), text_color=COLORS["text"]).pack(anchor="w", padx=30, pady=20)
        ctk.CTkLabel(graph_box, text="[ Gráfica de Actividad ]", font=("Inter", 18), text_color="#CBD5E1").place(relx=0.5, rely=0.5, anchor="center")

        # Sección de Últimos Accesos (Tabla)
        ctk.CTkLabel(main_scroll, text="🧾 Últimos Accesos Realizados", font=("Inter", 18, "bold"), text_color=COLORS["text"]).pack(anchor="w", padx=45, pady=(20, 10))
        
        self.contenedor_tabla = ctk.CTkFrame(main_scroll, fg_color=COLORS["card"], corner_radius=15, border_width=1, border_color=COLORS["border"])

        ctk.CTkLabel(graph_box, text="📈 Tendencia de Accesos por Hora", font=("Inter", 16, "bold"), text_color="#000000").pack(anchor="w", padx=30, pady=20)
        # -------- FILTRO DE FECHA --------
        self.fecha_var = ctk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))

        filtro_frame = ctk.CTkFrame(graph_box, fg_color="transparent")
        filtro_frame.pack(anchor="w", padx=30, pady=(0,10))

        ctk.CTkLabel(filtro_frame, text="Fecha:").pack(side="left", padx=5)

        self.calendario = DateEntry(
            filtro_frame,
            width=12,
            background="#3B82F6",
            foreground="white",
            borderwidth=2,
            date_pattern="yyyy-mm-dd"  # 👈 importante para que coincida con tus logs
        )
        self.calendario.pack(side="left", padx=5)
        self.calendario.bind("<<DateEntrySelected>>", lambda e: self.filtrar_por_fecha())

        self.calendario.configure(
            font=("Inter", 10),
            justify="center"
        )

        # contenedor solo para la gráfica
        self.graph_container = ctk.CTkFrame(graph_box, fg_color="transparent")
        self.graph_container.pack(fill="both", expand=True, padx=20, pady=10)

        self.filtrar_por_fecha()

        # Render inicial
        self.actualizar_grafica()

        # Sección de Últimos Accesos (Tabla)
        ctk.CTkLabel(main_scroll, text="🧾 Últimos Accesos Realizados", font=("Inter", 18, "bold"), text_color="#000000").pack(anchor="w", padx=45, pady=(20, 10))

        self.contenedor_tabla = ctk.CTkFrame(main_scroll, fg_color="white", corner_radius=15, border_width=1, border_color="#E2E8F0")

        self.contenedor_tabla.pack(fill="x", padx=40, pady=(0, 40))
        self.render_mini_tabla_accesos_data()

    def filtrar_por_fecha(self):
        fecha = self.calendario.get_date().strftime("%Y-%m-%d")
        self.fecha_var.set(fecha)  # sincroniza con tu variable
        self.actualizar_grafica()

    def render_grafica_accesos(self, container):
        from app.detection.detector_rostro import logs_accesos
        from datetime import datetime

        hoy = datetime.now().strftime("%Y-%m-%d")

        horas = list(range(24))
        conteo = [0] * 24

        for log in logs_accesos:
            if log["fecha"] == hoy:
                h = int(log["hora"])
                conteo[h] += 1

        fig = Figure(figsize=(6, 3), dpi=100)
        ax = fig.add_subplot(111)

        # Fondo limpio
        fig.patch.set_facecolor("#FFFFFF")
        ax.set_facecolor("#FFFFFF")

        # Barras modernas
        ax.bar(horas, conteo, color="#3B82F6", width=0.6)

        # Quitar bordes
        for spine in ["top", "right", "left", "bottom"]:
            ax.spines[spine].set_visible(False)

        # Grid suave
        ax.grid(axis='y', linestyle='--', alpha=0.2)

        # Ejes
        ax.set_xticks(horas)
        ax.set_xticklabels([f"{h:02d}" for h in horas], rotation=45, fontsize=8)

        ax.set_title("Accesos por hora", fontsize=12)
        ax.set_xlabel("")
        ax.set_ylabel("")

        ax.yaxis.set_major_locator(MaxNLocator(integer=True))

        canvas = FigureCanvasTkAgg(fig, master=container)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def actualizar_grafica(self):
        # limpiar SOLO la gráfica
        for widget in self.graph_container.winfo_children():
            widget.destroy()

        fecha = self.fecha_var.get()

        horas = list(range(24))
        conteo = [0] * 24

        for log in logs_accesos:
            if log["fecha"] == fecha:
                h = int(log["hora"])
                conteo[h] += 1

        fig = Figure(figsize=(6, 3), dpi=100)
        ax = fig.add_subplot(111)

        fig.patch.set_facecolor("#FFFFFF")
        ax.set_facecolor("#FFFFFF")

        ax.bar(horas, conteo, color="#3B82F6", width=0.6)

        for spine in ["top", "right", "left", "bottom"]:
            ax.spines[spine].set_visible(False)

        ax.grid(axis='y', linestyle='--', alpha=0.2)

        from matplotlib.ticker import MaxNLocator
        ax.yaxis.set_major_locator(MaxNLocator(integer=True))
        ax.set_yticks(range(0, max(conteo) + 2))

        ax.set_xticks(range(0, 24, 3))
        ax.set_xticklabels([f"{h}:00" for h in range(0, 24, 3)], fontsize=9)

        ax.set_title(f"Accesos del día {fecha}", fontsize=12)

        canvas = FigureCanvasTkAgg(fig, master=self.graph_container)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def render_mini_tabla_accesos_data(self):
        logs = [
            {"u": "MARÍA ELENA RODRÍGUEZ HERNÁNDEZ", "id_c": "31702938", "m": "MARIA.ROD@UNIV.MX", "ok": True},
            {"u": "JOSÉ LUIS PÉREZ RAMÍREZ", "id_c": "31702969", "m": "JOSE.PEREZ@UNIV.MX", "ok": False, "motivo": "⚠️ Rostro no reconocido"},
            {"u": "CARLOS ALBERTO MARTÍNEZ GARCÍA", "id_c": "31702945", "m": "CARLOS.M@UNIV.MX", "ok": True}
        ]
        for log in logs:
            row = ctk.CTkFrame(self.contenedor_tabla, fg_color="transparent", height=85)
            row.pack(fill="x", side="top"); row.pack_propagate(False)
            ctk.CTkLabel(row, text="👤", font=("Inter", 20)).pack(side="left", padx=20)
            mid = ctk.CTkFrame(row, fg_color="transparent")
            mid.pack(side="left", fill="both", expand=True)
            ctk.CTkLabel(mid, text=log["u"], font=("Inter", 13, "bold"), text_color=COLORS["text"]).pack(anchor="w", pady=(15,0))
            det = f"ID: {log['id_c']} • {log['m']}"
            if not log["ok"]: det += f"  {log.get('motivo', '')}"
            ctk.CTkLabel(mid, text=det, font=("Inter", 11), text_color=COLORS["subtext"]).pack(anchor="w")
            ctk.CTkFrame(self.contenedor_tabla, fg_color=COLORS["hover"], height=1).pack(fill="x", padx=20)

    # --- SIDEBAR ---
    def create_sidebar(self):
        sidebar = ctk.CTkFrame(self, width=280, corner_radius=0, fg_color=COLORS["sidebar"], border_width=1, border_color=COLORS["border"])
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_propagate(False)
        
        header = ctk.CTkFrame(sidebar, fg_color="transparent")
        header.pack(fill="x", pady=(15, 0), padx=15)
        # Se eliminó la línea de las 3 barras (☰)
        ctk.CTkLabel(header, text="K O D A", font=("Times New Roman", 38, "bold"), text_color="#3C054F").pack(side="left", padx=15)

        profile = ctk.CTkFrame(sidebar, fg_color="transparent")
        profile.pack(pady=(40, 15), padx=20, fill="x")
        ctk.CTkLabel(profile, text="👤", font=("Arial", 35)).pack(side="left")
        txt_info = ctk.CTkFrame(profile, fg_color="transparent")
        txt_info.pack(side="left", padx=10)
        ctk.CTkLabel(txt_info, text="ADMINISTRADOR", font=("Inter", 14, "bold"), text_color=COLORS["text"]).pack(anchor="w")
        ctk.CTkLabel(txt_info, text="Control Biométrico", font=("Inter", 11), text_color=COLORS["subtext"]).pack(anchor="w")

        self.btn_panel = self.crear_btn_sidebar(sidebar, "🏠   Panel de Control", self.mostrar_panel_control)
        self.btn_users = self.crear_btn_sidebar(sidebar, "👥   Gestión de Usuarios", self.mostrar_gestion_usuarios)
        self.btn_facultades = self.crear_btn_sidebar(sidebar, "🏫   Gestión de Facultades", self.mostrar_gestion_facultades)
        self.btn_carreras = self.crear_btn_sidebar(sidebar, "📚   Gestión de Carreras", self.mostrar_gestion_carreras)
        self.btn_account = self.crear_btn_sidebar(sidebar, "⚙️   Configuración Cuenta", self.mostrar_cuenta)

        ctk.CTkButton(sidebar, text="🚪 Cerrar Sesión", fg_color="transparent", text_color="#EF4444", 
                      font=("Inter", 14, "bold"), command=self.on_back).pack(side="bottom", pady=30, padx=20, fill="x")

    def create_stat_card(self, master, title, value, color):
        card = ctk.CTkFrame(master, height=100, fg_color=COLORS["card"], corner_radius=15, border_width=1, border_color=COLORS["border"])
        card.pack(side="left", padx=(0, 20), expand=True, fill="both")
        ctk.CTkLabel(card, text=title, font=("Inter", 12, "bold"), text_color=COLORS["text"]).pack(anchor="w", padx=20, pady=(15, 0))
        ctk.CTkLabel(card, text=value, font=("Inter", 28, "bold"), text_color=color).pack(anchor="w", padx=20)

    def crear_btn_sidebar(self, master, texto, comando):
        btn = ctk.CTkButton(master, text=texto, height=45, anchor="w", fg_color="transparent", 
                            text_color=COLORS["text"], hover_color=COLORS["hover"], font=("Inter", 16), command=comando)
        btn.pack(pady=6, padx=20, fill="x")
        return btn

    def create_top_controls(self, container):
        wrapper = ctk.CTkFrame(container, fg_color="transparent")
        wrapper.pack(side="right", padx=40, pady=20)
        
        # Switch de Tema
        t_f = ctk.CTkFrame(wrapper, fg_color="#E2E8F0", corner_radius=20, width=100, height=38)
        t_f.pack(side="left", padx=10); t_f.pack_propagate(False)
        ctk.CTkLabel(t_f, text="☀️", font=("Inter", 16)).place(x=20, y=19, anchor="center")
        self.theme_switch = ctk.CTkSwitch(t_f, text="", width=40, progress_color="#1D1D1F", command=self.toggle_theme)
        self.theme_switch.place(x=65, y=19, anchor="center")

        # Idioma
        l_c = ctk.CTkFrame(wrapper, fg_color="#E2E8F0", corner_radius=20, height=38)
        l_c.pack(side="left", padx=10)
        ctk.CTkLabel(l_c, text="🌐", font=("Inter", 16)).pack(side="left", padx=(12, 5))
        ctk.CTkButton(l_c, text="ES", width=38, height=28, corner_radius=14, fg_color="#1D1D1F", text_color="white").pack(side="left", padx=2, pady=5)
        ctk.CTkButton(l_c, text="EN", width=38, height=28, corner_radius=14, fg_color="transparent", text_color=COLORS["text"]).pack(side="left", padx=(2, 10), pady=5)