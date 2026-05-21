import customtkinter as ctk
import numpy as np
from scipy.interpolate import make_interp_spline
from matplotlib.figure import Figure
from matplotlib.ticker import MaxNLocator
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from app.views.user_management_view import UserManagementView
from app.views.account_view import AccountView 
from app.views.facultad_management_view import FacultadManagementView
from app.views.carrera_management_view import CarreraManagementView
from app.services.theme import COLORS
from app.views.app_context import AppContext
from datetime import datetime
from tkcalendar import DateEntry
from app.detection.detector_rostro import logs_accesos
from app.database.database import get_connection



class DashboardView(ctk.CTkFrame):
    def __init__(self, master, on_back):
        # Fondo general en gris muy claro
        super().__init__(master, fg_color=COLORS["bg"])
        self.is_compact = False
        # botones navegación (evita errores en responsive)
        
        self.btn_panel = None
        self.btn_users = None
        self.btn_facultades = None
        self.btn_carreras = None
        self.btn_account = None
        self.bind("<Configure>", self._on_resize)
        self.on_back = on_back

        # Configuración de pesos de la cuadrícula
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # 1. Sidebar (Lateral izquierda fija)
        

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

        if not self.is_compact:
            self.create_sidebar()
        # Cargar vista inicial
        self.mostrar_panel_control()




    def construir_menu(self, parent):
        # BOTONES (🔥 AQUÍ está el cambio)
        self.crear_btn_overlay(
            parent,
            "🏠 Panel de Control",
            self.mostrar_panel_control
        )

        self.crear_btn_overlay(
            parent,
            "👥 Gestion de Usuarios",
            self.mostrar_gestion_usuarios
        )

        self.crear_btn_overlay(
            parent,
            "🏫 Gestion de Facultades",
            self.mostrar_gestion_facultades
        )

        self.crear_btn_overlay(
            parent,
            "📚 Gestion de Carreras",
            self.mostrar_gestion_carreras
        )

        self.crear_btn_overlay(
            parent,
            "⚙️ Configuración",
            self.mostrar_cuenta
        )

        # LOGOUT
        ctk.CTkButton(
            parent,
            text="🚪 " + AppContext.t("Cerrar Sesión"),
            fg_color="transparent",
            text_color="#EF4444",
            command=self.on_back
        ).pack(side="bottom", pady=30, padx=20, fill="x")

    def toggle_sidebar_overlay(self):

        # Si ya está abierto, lo cierra
        if hasattr(self, "overlay_sidebar") and self.overlay_sidebar.winfo_exists():
            self.overlay_sidebar.destroy()
            return

        # Sidebar flotante, NO usa grid
        self.overlay_sidebar = ctk.CTkFrame(
            self,
            width=280,
            fg_color=COLORS["sidebar"],
            border_width=1,
            border_color=COLORS["border"],
            corner_radius=0
        )

        # Se pone encima sin mover nada
        self.overlay_sidebar.place(
            x=0,
            y=0,
            relheight=1
        )

        self.overlay_sidebar.lift()

        # HEADER con logo y botón cerrar
        header = ctk.CTkFrame(
            self.overlay_sidebar,
            fg_color="transparent",
            height=75
        )
        header.pack(fill="x", padx=15, pady=(10, 5))
        header.pack_propagate(False)

        ctk.CTkLabel(
            header,
            text="K O D A",
            font=("Times New Roman", 32, "bold"),
            text_color="#3C054F"
        ).pack(side="left", padx=(5, 0))

        ctk.CTkButton(
            header,
            text="☰",
            width=22,
            height=22,
            fg_color="transparent",
            text_color=COLORS["text"],
            hover_color=COLORS["hover"],
            font=("Inter", 14, "bold"),
            command=self.cerrar_overlay
        ).pack(side="right", padx=(0, 5), pady=5)

        # Menú
        self.construir_menu(self.overlay_sidebar)


    def crear_btn_overlay(self, master, texto, comando):
        ctk.CTkButton(
            master,
            text=texto,
            height=45,
            anchor="w",
            fg_color="transparent",
            text_color=COLORS["text"],
            hover_color=COLORS["hover"],
            command=lambda: [self.cerrar_overlay(), comando()]
        ).pack(fill="x", padx=20, pady=5)

    def cerrar_overlay(self):
        if hasattr(self, "overlay_sidebar") and self.overlay_sidebar.winfo_exists():
            self.overlay_sidebar.destroy()
            
            
            

    def toggle_sidebar(self):
        self.is_compact = not self.is_compact
        self.redibujar_layout()

    def _on_resize(self, event):
        new_mode = event.width < 900

        if new_mode != self.is_compact:
            self.is_compact = new_mode

            if hasattr(self, "_resize_job"):
                self.after_cancel(self._resize_job)

            self._resize_job = self.after(150, self.redibujar_layout)

    def redibujar_layout(self):
        self.cerrar_overlay()
        self.limpiar_derecha()

        # SOLO crear sidebar en modo normal
        if not self.is_compact:
            self.create_sidebar()
        else:
            # 📱 eliminar sidebar si existe
            if hasattr(self, 'sidebar_frame') and self.sidebar_frame.winfo_exists():
                self.sidebar_frame.destroy()

        self.create_top_controls(self.top_ctrl_area)

        # reset navegación
        self.btn_panel = None
        self.btn_users = None
        self.btn_facultades = None
        self.btn_carreras = None
        self.btn_account = None

        # recargar vista
        if hasattr(self, 'vista_actual_func') and self.vista_actual_func:
            self.after(50, self.vista_actual_func)
        else:
            self.after(50, self.mostrar_panel_control)
        
    

    def toggle_theme(self):
        if self.theme_switch.get() == 1:
            ctk.set_appearance_mode("dark")
        else:
            ctk.set_appearance_mode("light")
        
        self.actualizar_grafica()
        self.render_mini_tabla_accesos_data()

    def limpiar_derecha(self):
        """Elimina los widgets de la derecha para cargar una nueva vista"""
        for widget in self.content_container.winfo_children():
            widget.destroy()

    def actualizar_navegacion(self, btn_act):
        """Marca el botón seleccionado con colores oscuros para resaltar sobre el blanco"""
        btns = [self.btn_panel, self.btn_users, self.btn_facultades, self.btn_carreras, self.btn_account]
        for b in btns:
            if not b or not b.winfo_exists():
                continue

            if b == btn_act:
                # Botón Seleccionado: Azul muy oscuro con texto blanco
                b.configure(fg_color=COLORS["selected"], text_color=("white", "black"), hover_color=COLORS["selected"])
            else:
                # Botones Inactivos: Transparentes con texto negro
                b.configure(fg_color="transparent", text_color=COLORS["text"], hover_color="#F1F5F9")

    # --- MÉTODOS DE NAVEGACIÓN ---
    def mostrar_panel_control(self):
        self.vista_actual_func = self.mostrar_panel_control
        self.limpiar_derecha()
        if not self.is_compact:  # 👈 SOLO esto agregas
            self.actualizar_navegacion(self.btn_panel)
        self.render_dashboard_principal()

    def mostrar_gestion_usuarios(self):
        self.vista_actual_func = self.mostrar_gestion_usuarios
        self.limpiar_derecha()
        if not self.is_compact:  # 👈 SOLO esto agregas
            self.actualizar_navegacion(self.btn_users)
        UserManagementView(self.content_container).pack(fill="both", expand=True, padx=40)

    def mostrar_gestion_facultades(self):
        self.vista_actual_func = self.mostrar_gestion_facultades
        self.limpiar_derecha()
        if not self.is_compact:  # 👈 SOLO esto agregas
            self.actualizar_navegacion(self.btn_facultades)
        FacultadManagementView(self.content_container).pack(fill="both", expand=True, padx=40)

    def mostrar_gestion_carreras(self):
        self.vista_actual_func = self.mostrar_gestion_carreras
        self.limpiar_derecha()
        if not self.is_compact:  # 👈 SOLO esto agregas
            self.actualizar_navegacion(self.btn_carreras)
        CarreraManagementView(self.content_container).pack(fill="both", expand=True, padx=40)

    def mostrar_cuenta(self):
        self.vista_actual_func = self.mostrar_cuenta
        self.limpiar_derecha()
        if not self.is_compact:  # 👈 SOLO esto agregas
            self.actualizar_navegacion(self.btn_account)
        AccountView(self.content_container, on_logout=self.on_back).pack(fill="both", expand=True, padx=40)



    def obtener_estadisticas_dashboard(self):
        conn = get_connection()
        cursor = conn.cursor()

        hoy = datetime.now().strftime("%Y-%m-%d")

        cursor.execute("SELECT COUNT(*) FROM usuario")
        total_registros = cursor.fetchone()[0]

        cursor.execute("""
            SELECT COUNT(*) 
            FROM registro_acceso
            WHERE DATE(fecha_hora) = ?
        """, (hoy,))
        accesos_hoy = cursor.fetchone()[0]

        cursor.execute("""
            SELECT COUNT(*) 
            FROM registro_acceso
            WHERE DATE(fecha_hora) = ?
            AND resultado = 1
        """, (hoy,))
        autorizados = cursor.fetchone()[0]

        cursor.execute("""
            SELECT COUNT(*) 
            FROM registro_acceso
            WHERE DATE(fecha_hora) = ?
            AND resultado = 0
        """, (hoy,))
        denegados = cursor.fetchone()[0]

        conn.close()

        return total_registros, accesos_hoy, autorizados, denegados
    
    
    # --- RENDERIZADO DEL PANEL DE CONTROL (DASHBOARD) ---
    def render_dashboard_principal(self):
        
        padx_main = 15 if self.is_compact else 40

        main_scroll = ctk.CTkScrollableFrame(self.content_container, fg_color="transparent")
        main_scroll.pack(fill="both", expand=True)

        # Header del Dashboard
        header = ctk.CTkFrame(main_scroll, fg_color="transparent")
        header.pack(fill="x", padx=padx_main, pady=(10, 20))
        ctk.CTkLabel(header, text="🏠  " + AppContext.t("Panel de Control"), font=("Inter", 28, "bold"), text_color=COLORS["text"]).pack(anchor="w")
        ctk.CTkLabel(header, text=AppContext.t("Resumen general y actividad reciente"), font=("Inter", 16), text_color=COLORS["subtext"]).pack(anchor="w")

        # Tarjetas de Estadísticas (Stats)
        stats_frame = ctk.CTkFrame(main_scroll, fg_color="transparent")
        stats_frame.pack(fill="x", padx=padx_main, pady=10)
        if self.is_compact:
            stats_frame.grid_columnconfigure(0, weight=1)
            stats_frame.grid_columnconfigure(1, weight=1)

        total_registros, accesos_hoy, autorizados, denegados = self.obtener_estadisticas_dashboard()

        self.create_stat_card(stats_frame, "👥 " + AppContext.t("Total Registros"), str(total_registros), "#3B82F6", 0)
        self.create_stat_card(stats_frame, "🕒 " + AppContext.t("Accesos Hoy"), str(accesos_hoy), "#6366F1", 1)
        self.create_stat_card(stats_frame, "✅ " + AppContext.t("Autorizados"), str(autorizados), "#10B981", 2)
        self.create_stat_card(stats_frame, "🚫 " + AppContext.t("Denegados"), str(denegados), "#EF4444", 3)
        
        # Contenedor de la Gráfica
        graph_box = ctk.CTkFrame(main_scroll, fg_color=COLORS["card"], corner_radius=20, border_width=1, border_color=COLORS["border"], height=280)
        graph_box.pack(fill="x", padx=40, pady=20)
        graph_box.pack_propagate(False)

        
        ctk.CTkLabel(graph_box, text="📈 Tendencia de Accesos por Hora", font=("Inter", 18, "bold"), text_color=COLORS["text"]).pack(anchor="w", padx=30, pady=20)
        # -------- FILTRO DE FECHA --------
        self.fecha_var = ctk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))

        filtro_frame = ctk.CTkFrame(graph_box, fg_color="transparent")
        filtro_frame.pack(anchor="w", padx=30, pady=(0, 10))

        ctk.CTkLabel(filtro_frame, text=AppContext.t("Fecha:")).pack(side="left", padx=5)

        self.calendario = DateEntry(
            filtro_frame,
            width=12,
            background="#3B82F6",
            foreground="white",
            borderwidth=2,
            date_pattern="yyyy-mm-dd"
        )
        self.calendario.pack(side="left", padx=5)
        self.calendario.bind("<<DateEntrySelected>>", lambda e: self.filtrar_por_fecha())

        self.calendario.configure(
            font=("Inter", 10),
            justify="center"
        )

        # Contenedor solo para la gráfica
        self.graph_container = ctk.CTkFrame(graph_box, fg_color="transparent")
        self.graph_container.pack(fill="both", expand=True, padx=20, pady=10)

        self.filtrar_por_fecha()

        # Render inicial
        

        # Sección de Últimos Accesos (Tabla)
        # Sección de Últimos Accesos (Tabla)

        header_tabla = ctk.CTkFrame(main_scroll, fg_color="transparent")
        header_tabla.pack(fill="x", padx=75, pady=(20, 10))

        ctk.CTkLabel(
            header_tabla,
            text=AppContext.t("Registro de últimos accesos"),
            font=("Inter", 18, "bold"),
            text_color=COLORS["text"]
        ).pack(anchor="w")

        self.contenedor_tabla = ctk.CTkFrame(
            main_scroll,
            fg_color="white",
            corner_radius=15,
            border_width=1,
            border_color="#E2E8F0"
        )

        self.contenedor_tabla.pack(fill="x", padx=40, pady=(0, 40))
        self.render_mini_tabla_accesos_data()

    def filtrar_por_fecha(self):
        fecha = self.calendario.get_date().strftime("%Y-%m-%d")
        self.fecha_var.set(fecha)
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

        fig.patch.set_facecolor("#FFFFFF")
        ax.set_facecolor("#FFFFFF")

        ax.bar(horas, conteo, color="#3B82F6", width=0.6)

        for spine in ["top", "right", "left", "bottom"]:
            ax.spines[spine].set_visible(False)

        ax.grid(axis='y', linestyle='--', alpha=0.2)

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
        if not self.winfo_exists():
            return

        if not hasattr(self, "graph_container"):
            return

        if not self.graph_container.winfo_exists():
            return

        for widget in self.graph_container.winfo_children():
            widget.destroy()

        fecha = self.fecha_var.get()

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT 
                CAST(strftime('%H', fecha_hora) AS INTEGER) AS hora,
                COUNT(*) AS total
            FROM registro_acceso
            WHERE DATE(fecha_hora) = ?
            GROUP BY hora
            ORDER BY hora
        """, (fecha,))

        filas = cursor.fetchall()
        conn.close()

        horas = list(range(24))
        conteo = [0] * 24

        for fila in filas:
            conteo[int(fila[0])] = int(fila[1])

        mode = ctk.get_appearance_mode()
        bg_color = "#1E293B" if mode == "Dark" else "#FFFFFF"
        text_color = "#F8FAFC" if mode == "Dark" else "#0F172A"
        grid_color = "#334155" if mode == "Dark" else "#E2E8F0"
        line_color = "#3B82F6"

        fig = Figure(figsize=(7, 3.2), dpi=100)
        ax = fig.add_subplot(111)

        fig.patch.set_facecolor(bg_color)
        ax.set_facecolor(bg_color)

        x = np.array(horas)
        y = np.array(conteo)

        if sum(conteo) > 0:
            x_smooth = np.linspace(x.min(), x.max(), 300)
            spl = make_interp_spline(x, y, k=3)
            y_smooth = np.clip(spl(x_smooth), 0, None)

            ax.fill_between(x_smooth, y_smooth, color=line_color, alpha=0.22)
            ax.plot(x_smooth, y_smooth, color=line_color, linewidth=2.8)

            ax.scatter(
                x,
                y, 
                s=28,
                color=line_color,
                edgecolors=bg_color,
                linewidths=1.2,
                zorder=3
            )
        else:
            ax.plot(horas, conteo, color=line_color, linewidth=2.5, alpha=0.6)

            ax.text(
                0.5,
                0.5,
                "Sin accesos registrados en esta fecha",
                transform=ax.transAxes,
                ha="center",
                va="center",
                fontsize=11,
                color=text_color,
                alpha=0.7
            )

        ax.set_xlim(0, 23)
        ax.set_ylim(bottom=0)

        max_y = max(conteo) if conteo else 0
        ax.set_ylim(0, max(3, max_y + 1))

        ax.set_xticks([0, 3, 6, 9, 12, 15, 18, 21, 23])
        ax.set_xticklabels(
            ["00:00", "03:00", "06:00", "09:00", "12:00", "15:00", "18:00", "21:00", "23:00"],
            fontsize=9,
            color=text_color
        )

        ax.yaxis.set_major_locator(MaxNLocator(integer=True))
        ax.tick_params(axis="y", colors=text_color, labelsize=9)

        ax.grid(axis="y", linestyle="--", alpha=0.25, color=grid_color)
        ax.grid(axis="x", visible=False)

        for spine in ax.spines.values():
            spine.set_visible(False)

        ax.set_xlabel("")
        ax.set_ylabel("")

        fig.tight_layout(pad=1.4)

        canvas = FigureCanvasTkAgg(fig, master=self.graph_container)
        canvas.draw()

        widget = canvas.get_tk_widget()
        widget.configure(bg=bg_color, highlightthickness=0)
        widget.pack(fill="both", expand=True)
        
    def render_mini_tabla_accesos_data(self):
        if not hasattr(self, "contenedor_tabla"):
            return

        if not self.contenedor_tabla.winfo_exists():
            return

        for widget in self.contenedor_tabla.winfo_children():
            widget.destroy()

        mode = ctk.get_appearance_mode()
        bg_color = "#1E293B" if mode == "Dark" else "#FFFFFF"
        row_color = "#0F172A" if mode == "Dark" else "#F8FAFC"
        text_color = "#F8FAFC" if mode == "Dark" else "#0F172A"
        subtext_color = "#CBD5E1" if mode == "Dark" else "#64748B"
        border_color = "#334155" if mode == "Dark" else "#E2E8F0"

        self.contenedor_tabla.configure(
            fg_color=bg_color,
            border_color=border_color
        )

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT 
                r.id_registro,
                r.fecha_hora,
                r.resultado,
                r.motivo,
                u.nombre,
                u.a_paterno,
                u.a_materno,
                u.cuenta,
                u.correo
            FROM registro_acceso r
            LEFT JOIN usuario u ON r.id_usuario = u.id_usuario
            ORDER BY r.fecha_hora DESC
            LIMIT 10
        """)

        registros = cursor.fetchall()
        conn.close()

        if not registros:
            ctk.CTkLabel(
                self.contenedor_tabla,
                text="Sin accesos registrados",
                font=("Inter", 13),
                text_color=subtext_color
            ).pack(pady=30)
            return

        for reg in registros:
            _, fecha_hora, resultado, motivo, nombre, ap, am, cuenta, correo = reg

            ok = int(resultado) == 1

            nombre_completo = (
                f"{nombre or ''} {ap or ''} {am or ''}".strip().upper()
                if nombre else "USUARIO NO REGISTRADO"
            )

            cuenta_txt = cuenta if cuenta else "Sin cuenta"
            correo_txt = correo if correo else "Sin correo"
            motivo_txt = motivo if motivo else ("Acceso autorizado" if ok else "Acceso denegado")

            card = ctk.CTkFrame(
                self.contenedor_tabla,
                fg_color=row_color,
                corner_radius=12,
                border_width=1,
                border_color=border_color
            )
            card.pack(fill="x", padx=16, pady=8)

            top = ctk.CTkFrame(card, fg_color="transparent")
            top.pack(fill="x", padx=14, pady=(12, 4))

            ctk.CTkLabel(
                top,
                text="✅" if ok else "🚫",
                font=("Inter", 22)
            ).pack(side="left", padx=(0, 10))

            info = ctk.CTkFrame(top, fg_color="transparent")
            info.pack(side="left", fill="x", expand=True)

            ctk.CTkLabel(
                info,
                text=nombre_completo,
                font=("Inter", 13, "bold"),
                text_color=text_color,
                anchor="w"
            ).pack(anchor="w", fill="x")

            ctk.CTkLabel(
                info,
                text=f"ID: {cuenta_txt}  •  {correo_txt}",
                font=("Inter", 11),
                text_color=subtext_color,
                anchor="w"
            ).pack(anchor="w", fill="x")

            badge = ctk.CTkFrame(
                top,
                fg_color="#D1FAE5" if ok else "#FEE2E2",
                corner_radius=16
            )
            badge.pack(side="right")

            ctk.CTkLabel(
                badge,
                text="AUTORIZADO" if ok else "DENEGADO",
                font=("Inter", 9, "bold"),
                text_color="#065F46" if ok else "#991B1B"
            ).pack(padx=10, pady=4)

            bottom = ctk.CTkFrame(card, fg_color="transparent")
            bottom.pack(fill="x", padx=14, pady=(0, 12))

            ctk.CTkLabel(
                bottom,
                text=f"🕒 {fecha_hora}   •   {motivo_txt}",
                font=("Inter", 10),
                text_color=subtext_color,
                anchor="w"
            ).pack(anchor="w")
    
    
    
    
    # --- SIDEBAR ---
    def create_sidebar(self):
        self.sidebar_frame = ctk.CTkFrame(self, width=280, corner_radius=0, fg_color=COLORS["sidebar"], border_width=1, border_color=COLORS["border"])
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_propagate(False)
        
        header = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        header.pack(fill="x", pady=(15, 0), padx=15)
        # Se eliminó la línea de las 3 barras (☰)
        ctk.CTkLabel(header, text="K O D A", font=("Times New Roman", 38, "bold"), text_color="#3C054F").pack(side="left", padx=15)


        if not self.is_compact:
            profile = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
            profile.pack(pady=(40, 15), padx=20, fill="x")
            ctk.CTkLabel(profile, text="👤", font=("Arial", 35)).pack(side="left")
            txt_info = ctk.CTkFrame(profile, fg_color="transparent")
            txt_info.pack(side="left", padx=10)
        
            # Textos traducidos del perfil
            ctk.CTkLabel(txt_info, text=AppContext.t("ADMINISTRADOR"), font=("Inter", 14, "bold"), text_color=COLORS["text"]).pack(anchor="w")
            ctk.CTkLabel(txt_info, text=AppContext.t("Control Biométrico"), font=("Inter", 11), text_color=COLORS["subtext"]).pack(anchor="w")

        self.btn_panel = self.crear_btn_sidebar(self.sidebar_frame, "🏠   Panel de Control", self.mostrar_panel_control)
        self.btn_users = self.crear_btn_sidebar(self.sidebar_frame, "👥   Gestión de Usuarios", self.mostrar_gestion_usuarios)
        self.btn_facultades = self.crear_btn_sidebar(self.sidebar_frame, "🏫   Gestión de Facultades", self.mostrar_gestion_facultades)
        self.btn_carreras = self.crear_btn_sidebar(self.sidebar_frame, "📚   Gestión de Carreras", self.mostrar_gestion_carreras)
        self.btn_account = self.crear_btn_sidebar(self.sidebar_frame, "⚙️   Configuración Cuenta", self.mostrar_cuenta)

        ctk.CTkButton(self.sidebar_frame, text="🚪 Cerrar Sesión", fg_color="transparent", text_color="#EF4444", 
                      font=("Inter", 14, "bold"), command=self.on_back).pack(side="bottom", pady=30, padx=20, fill="x")

    def create_stat_card(self, master, title, value, color, index):
        card = ctk.CTkFrame(
            master,
            height=100,
            fg_color=COLORS["card"],
            corner_radius=15,
            border_width=1,
            border_color=COLORS["border"]
        )

        if self.is_compact:
            card.configure(height=80)

        if self.is_compact:
            # 📱 GRID 2x2
            row = index // 2
            col = index % 2

            card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
        else:
            # 💻 NORMAL
            card.pack(side="left", padx=(0, 20), expand=True, fill="both")

        ctk.CTkLabel(card, text=title, font=("Inter", 12, "bold"),
                    text_color=COLORS["text"]).pack(anchor="w", padx=20, pady=(15, 0))

        ctk.CTkLabel(card, text=value, font=("Inter", 28, "bold"),
                    text_color=color).pack(anchor="w", padx=20)
    

    def crear_btn_sidebar(self, master, texto, comando):
        btn = ctk.CTkButton(master, text=texto, height=45, anchor="w", fg_color="transparent", 
                            text_color=COLORS["text"], hover_color=COLORS["hover"], font=("Inter", 16), command=comando)
        btn.pack(pady=6, padx=20, fill="x")
        return btn
    
    def create_top_controls(self, container):
        # Limpiamos contenedor por si se está redibujando tras cambio de idioma
        for widget in container.winfo_children():
            widget.destroy()

        if self.is_compact:
            ctk.CTkButton(
                container,
                text="☰",
                width=40,
                height=40,
                fg_color="transparent",
                text_color=COLORS["text"],
                command=self.toggle_sidebar_overlay
            ).pack(side="left", padx=20)

        wrapper = ctk.CTkFrame(container, fg_color="transparent")
        wrapper.pack(side="right", padx=40, pady=20)

        # Switch de Tema
        t_f = ctk.CTkFrame(wrapper, fg_color="#E2E8F0", corner_radius=20, width=100, height=38)
        t_f.pack(side="left", padx=10)
        t_f.pack_propagate(False)
        ctk.CTkLabel(t_f, text="☀️", font=("Inter", 16)).place(x=20, y=19, anchor="center")
        self.theme_switch = ctk.CTkSwitch(t_f, text="", width=40, progress_color="#1D1D1F", command=self.toggle_theme)
        
        # Mantener el estado visual del switch de tema
        if ctk.get_appearance_mode() == "Dark":
            self.theme_switch.select()
        else:
            self.theme_switch.deselect()
            
        self.theme_switch.place(x=65, y=19, anchor="center")

        # Idioma
        l_c = ctk.CTkFrame(wrapper, fg_color="#E2E8F0", corner_radius=20, height=38)
        l_c.pack(side="left", padx=10)
        ctk.CTkLabel(l_c, text="🌐", font=("Inter", 16)).pack(side="left", padx=(12, 5))
        
        # Determinar colores de los botones activos
        color_es = "#1D1D1F" if AppContext.idioma_actual == "es" else "transparent"
        txt_es = "white" if AppContext.idioma_actual == "es" else COLORS["text"]
        color_en = "#1D1D1F" if AppContext.idioma_actual == "en" else "transparent"
        txt_en = "white" if AppContext.idioma_actual == "en" else COLORS["text"]

        # Botones con el comando asignado
        ctk.CTkButton(l_c, text="ES", width=38, height=28, corner_radius=14, fg_color=color_es, text_color=txt_es, 
                      command=lambda: self.cambiar_idioma_dashboard("es")).pack(side="left", padx=2, pady=5)
        ctk.CTkButton(l_c, text="EN", width=38, height=28, corner_radius=14, fg_color=color_en, text_color=txt_en, 
                      command=lambda: self.cambiar_idioma_dashboard("en")).pack(side="left", padx=(2, 10), pady=5)

    # --- NUEVOS MÉTODOS DE IDIOMA ---
    def cambiar_idioma_dashboard(self, nuevo_idioma):
        """Método llamado por los botones de la barra superior"""
        if AppContext.idioma_actual == nuevo_idioma:
            return
        AppContext.set_idioma(nuevo_idioma)
        self.refrescar_idioma_completo()

    def refrescar_idioma_completo(self):
        """Destruye y redibuja la barra lateral, la superior y la vista activa"""
        self.create_sidebar()
        self.create_top_controls(self.top_ctrl_area)
        
        # Volver a cargar la pantalla en la que el usuario estaba
        if hasattr(self, 'vista_actual_func'):
            self.vista_actual_func()