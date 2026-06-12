import os
import customtkinter as ctk
import numpy as np
from scipy.interpolate import make_interp_spline
from matplotlib.figure import Figure
from matplotlib.ticker import MaxNLocator
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from app.views.user_management_view import UserManagementView
from app.views.account_view import AccountView, _cargar_datos
from app.views.area_management_view import AreaManagementView
from app.views.puesto_management_view import PuestoManagementView
from app.services.theme import COLORS
from app.views.app_context import AppContext
from datetime import datetime
from tkcalendar import DateEntry
from app.detection.detector_rostro import logs_accesos
from app.database.database import get_connection

class DashboardView(ctk.CTkFrame):
    def __init__(self, master, on_back):
        super().__init__(master, fg_color=COLORS["bg"])
        self.is_compact = False
        self.is_sidebar_open = False
        self._resize_job = None
        self._view_job = None

        self.btn_panel      = None
        self.btn_users      = None
        self.btn_areas = None
        self.btn_puestos   = None
        self.btn_account    = None
        self.bind("<Configure>", self._on_resize)
        self.on_back = on_back

        # Referencia a imagen del sidebar para evitar garbage collection
        self._sidebar_ctk_img = None

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)
        self.grid_rowconfigure(0, weight=1)

        self.right_panel = ctk.CTkFrame(self, fg_color="transparent")
        self.right_panel.grid(row=0, column=0, columnspan=2, sticky="nsew")

        self.top_ctrl_area = ctk.CTkFrame(self.right_panel, fg_color="transparent", height=self._topbar_height())
        self.top_ctrl_area.pack(side="top", fill="x")
        self.top_ctrl_area.pack_propagate(False)
        self.create_top_controls(self.top_ctrl_area)

        self.content_container = ctk.CTkFrame(self.right_panel, fg_color="transparent")
        self.content_container.pack(fill="both", expand=True)

        self.mostrar_panel_control()

    def _apply_shell_layout(self):
        if self.is_compact:
            if self.is_sidebar_open:
                self.grid_columnconfigure(0, weight=0)
                self.grid_columnconfigure(1, weight=1)
                self.right_panel.grid(row=0, column=1, columnspan=1, sticky="nsew")
            else:
                self.grid_columnconfigure(0, weight=1)
                self.grid_columnconfigure(1, weight=0)
                self.right_panel.grid(row=0, column=0, columnspan=2, sticky="nsew")
        else:
            self.grid_columnconfigure(0, weight=1)
            self.grid_columnconfigure(1, weight=0)
            self.right_panel.grid(row=0, column=0, columnspan=2, sticky="nsew")

    def _topbar_height(self):
        return 108 if self.is_compact else 78

    def _cancel_pending_jobs(self):
        for attr in ("_resize_job", "_view_job"):
            job = getattr(self, attr, None)
            if job:
                try:
                    self.after_cancel(job)
                except Exception:
                    pass
                setattr(self, attr, None)
    
    def construir_menu(self, parent):
        self.crear_btn_overlay(parent, AppContext.t("Panel de Control"),      self.mostrar_panel_control)
        self.crear_btn_overlay(parent, AppContext.t("GestiÃ³n de Usuarios"),   self.mostrar_gestion_usuarios)
        self.crear_btn_overlay(parent, AppContext.t("GestiÃ³n de Facultades"), self.mostrar_gestion_areas)
        self.crear_btn_overlay(parent, AppContext.t("GestiÃ³n de Carreras"),   self.mostrar_gestion_puestos)
        self.crear_btn_overlay(parent, AppContext.t("ConfiguraciÃ³n"),         self.mostrar_cuenta)

        ctk.CTkButton(
            parent,
            text=AppContext.t("Cerrar SesiÃ³n"),
            fg_color="transparent",
            text_color="#EF4444",
            command=self.on_back
        ).pack(side="bottom", pady=30, padx=20, fill="x")
    
    def toggle_sidebar_overlay(self):
        if not self.is_compact:
            return

        self.is_sidebar_open = not self.is_sidebar_open
        if self.is_sidebar_open:
            self.create_sidebar()
        else:
            self.cerrar_overlay()
        self._apply_shell_layout()
    
    def crear_btn_overlay(self, master, texto, comando):
        ctk.CTkButton(
            master, text=texto, height=36, anchor="w",
            fg_color="transparent", text_color=COLORS["text"],
            hover_color=COLORS["hover"],
            command=lambda: [self.cerrar_overlay(), comando()]
        ).pack(fill="x", padx=20, pady=5)

    def cerrar_overlay(self):
        self.is_sidebar_open = False
        for attr in ("overlay_sidebar", "sidebar_frame"):
            widget = getattr(self, attr, None)
            if widget and widget.winfo_exists():
                widget.destroy()
        if hasattr(self, "right_panel") and self.right_panel.winfo_exists():
            self._apply_shell_layout()

    # -------------------------------------------------------------
    # RESIZE
    # -------------------------------------------------------------
    def toggle_sidebar(self):
        self.is_compact = not self.is_compact
        self.redibujar_layout()

    def _on_resize(self, event):
        new_mode = event.width < 1050
        if new_mode != self.is_compact:
            self.is_compact = new_mode
            if hasattr(self, "top_ctrl_area") and self.top_ctrl_area.winfo_exists():
                self.top_ctrl_area.configure(height=self._topbar_height())
            if getattr(self, "_resize_job", None):
                self.after_cancel(self._resize_job)
            self._resize_job = self.after(150, self.redibujar_layout)

    def redibujar_layout(self):
        self._cancel_pending_jobs()
        self.cerrar_overlay()
        self.limpiar_derecha()

        if hasattr(self, 'sidebar_frame') and self.sidebar_frame.winfo_exists():
            self.sidebar_frame.destroy()
        self._apply_shell_layout()

        self.btn_panel      = None
        self.btn_users      = None
        self.btn_areas = None
        self.btn_puestos   = None
        self.btn_account    = None

        self.top_ctrl_area.configure(height=self._topbar_height())
        self.create_top_controls(self.top_ctrl_area)

        if hasattr(self, 'vista_actual_func') and self.vista_actual_func:
            self._view_job = self.after(50, self._render_current_view)
        else:
            self._view_job = self.after(50, self.mostrar_panel_control)

    def _render_current_view(self):
        self._view_job = None
        if self.winfo_exists() and hasattr(self, 'vista_actual_func') and self.vista_actual_func:
            self.vista_actual_func()
    
    def toggle_theme(self):
        if self.theme_switch.get() == 1:
            ctk.set_appearance_mode("dark")
        else:
            ctk.set_appearance_mode("light")
        self.refrescar_idioma_completo()

    def limpiar_derecha(self):
        self._cancel_pending_jobs()
        for widget in self.content_container.winfo_children():
            if widget.winfo_exists():
                widget.destroy()

    def actualizar_navegacion(self, btn_act):
        btns = [self.btn_panel, self.btn_users, self.btn_areas, self.btn_puestos, self.btn_account]
        for b in btns:
            if not b or not b.winfo_exists():
                continue
            if b == btn_act:
                b.configure(fg_color=COLORS["accent"], text_color="#111827", hover_color=COLORS["accent_hover"])
            else:
                b.configure(fg_color="#162033", text_color=COLORS["sidebar_text"], hover_color="#22304A")

    # -------------------------------------------------------------
    # NAVEGACIï¿½N
    # -------------------------------------------------------------
    def mostrar_panel_control(self):
        self.vista_actual_func = self.mostrar_panel_control
        self.limpiar_derecha()
        self.actualizar_navegacion(self.btn_panel)
        self.render_dashboard_principal()

    def mostrar_gestion_usuarios(self):
        self.vista_actual_func = self.mostrar_gestion_usuarios
        self.limpiar_derecha()
        self.actualizar_navegacion(self.btn_users)
        UserManagementView(self.content_container).pack(fill="both", expand=True, padx=4 if self.is_compact else 20)

    def mostrar_gestion_areas(self):
        self.vista_actual_func = self.mostrar_gestion_areas
        self.limpiar_derecha()
        self.actualizar_navegacion(self.btn_areas)
        AreaManagementView(self.content_container).pack(fill="both", expand=True, padx=4 if self.is_compact else 20)

    def mostrar_gestion_puestos(self):
        self.vista_actual_func = self.mostrar_gestion_puestos
        self.limpiar_derecha()
        self.actualizar_navegacion(self.btn_puestos)
        PuestoManagementView(self.content_container).pack(fill="both", expand=True, padx=4 if self.is_compact else 20)

    def mostrar_cuenta(self):
        self.vista_actual_func = self.mostrar_cuenta
        self.limpiar_derecha()
        self.actualizar_navegacion(self.btn_account)
        AccountView(
            self.content_container,
            on_logout=self.on_back,
            on_profile_updated=self._refrescar_perfil_sidebar,  # ? NUEVO
        ).pack(fill="both", expand=True, padx=4 if self.is_compact else 20)

    # -------------------------------------------------------------
    # ACTUALIZAR SIDEBAR CON PERFIL  ? NUEVO
    # -------------------------------------------------------------
    def _refrescar_perfil_sidebar(self):
        """Reconstruye el sidebar para mostrar nombre y foto actualizados."""
        self.create_top_controls(self.top_ctrl_area)
        if self.btn_account and self.btn_account.winfo_exists():
            self.actualizar_navegacion(self.btn_account)

    # -------------------------------------------------------------
    # ESTADï¿½STICAS
    # -------------------------------------------------------------
    def obtener_estadisticas_dashboard(self):
        conn = get_connection()
        cursor = conn.cursor()
        hoy = datetime.now().strftime("%Y-%m-%d")

        cursor.execute("SELECT COUNT(*) FROM usuario")
        total_registros = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM registro_acceso WHERE DATE(fecha_hora) = ?", (hoy,))
        accesos_hoy = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM registro_acceso WHERE DATE(fecha_hora) = ? AND resultado = 1", (hoy,))
        autorizados = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM registro_acceso WHERE DATE(fecha_hora) = ? AND resultado = 0", (hoy,))
        denegados = cursor.fetchone()[0]

        conn.close()
        return total_registros, accesos_hoy, autorizados, denegados
    
    def render_dashboard_principal(self):
        padx_main = 6 if self.is_compact else 18

        main_scroll = ctk.CTkScrollableFrame(self.content_container, fg_color="transparent")
        main_scroll.pack(fill="both", expand=True)

        total_registros, accesos_hoy, autorizados, denegados = self.obtener_estadisticas_dashboard()
        tasa = 0 if accesos_hoy == 0 else int((autorizados / max(accesos_hoy, 1)) * 100)

        header = ctk.CTkFrame(main_scroll, fg_color="transparent")
        header.pack(fill="x", padx=padx_main, pady=(8 if self.is_compact else 14, 5))
        ctk.CTkLabel(
            header,
            text=AppContext.t("Tablero operativo"),
            font=("Inter", 20 if self.is_compact else 28, "bold"),
            text_color=COLORS["text"],
        ).pack(side="left", anchor="w")
        if not self.is_compact:
            ctk.CTkLabel(
                header,
                text=datetime.now().strftime("%d/%m/%Y"),
                font=("Inter", 13, "bold"),
                text_color=COLORS["subtext"],
            ).pack(side="right", anchor="e", pady=(10, 0))

        layout = ctk.CTkFrame(main_scroll, fg_color="transparent")
        layout.pack(fill="both", expand=True, padx=padx_main, pady=(4, 10))
        if not self.is_compact:
            layout.grid_columnconfigure(0, weight=0)
            layout.grid_columnconfigure(1, weight=1)
            layout.grid_rowconfigure(0, weight=1)

        left_panel = ctk.CTkFrame(
            layout,
            fg_color=COLORS["sidebar"],
            corner_radius=8,
            width=270,
            height=280 if self.is_compact else 430,
            border_width=1,
            border_color="#22304A",
        )
        if self.is_compact:
            left_panel.pack(fill="x", pady=(0, 12))
        else:
            left_panel.grid(row=0, column=0, sticky="nsw", padx=(0, 16))
        left_panel.pack_propagate(False)

        left_body = ctk.CTkFrame(left_panel, fg_color="transparent")
        left_body.pack(fill="both", expand=True, padx=12, pady=12)

        ctk.CTkLabel(
            left_body,
            text=AppContext.t("Turno activo").upper(),
            font=("Inter", 10, "bold"),
            text_color=COLORS["accent"],
        ).pack(anchor="w")
        ctk.CTkLabel(
            left_body,
            text=f"{tasa}%",
            font=("Inter", 38 if not self.is_compact else 30, "bold"),
            text_color="#FFFFFF",
        ).pack(anchor="w", pady=(6, 0))
        ctk.CTkLabel(
            left_body,
            text=AppContext.t("Tasa de accesos autorizados hoy"),
            font=("Inter", 12),
            text_color=COLORS["sidebar_muted"],
            wraplength=250,
            justify="left",
        ).pack(anchor="w", pady=(0, 10))

        metricas = [
            (AppContext.t("Personal"), total_registros, COLORS["primary"]),
            (AppContext.t("Eventos"), accesos_hoy, COLORS["info"]),
            (AppContext.t("Validos"), autorizados, COLORS["success"]),
            (AppContext.t("Alertas"), denegados, COLORS["danger"]),
        ]
        for titulo, valor, color in metricas:
            row = ctk.CTkFrame(left_body, fg_color="#111C31", corner_radius=8)
            row.pack(fill="x", pady=3)
            ctk.CTkFrame(row, fg_color=color, width=4, corner_radius=0).pack(side="left", fill="y")
            ctk.CTkLabel(
                row,
                text=titulo,
                font=("Inter", 12, "bold"),
                text_color=COLORS["sidebar_muted"],
            ).pack(side="left", padx=10, pady=7)
            ctk.CTkLabel(
                row,
                text=str(valor),
                font=("Inter", 17, "bold"),
                text_color="#FFFFFF",
            ).pack(side="right", padx=10, pady=5)

        right_panel = ctk.CTkFrame(layout, fg_color="transparent")
        if self.is_compact:
            right_panel.pack(fill="both", expand=True)
        else:
            right_panel.grid(row=0, column=1, sticky="nsew")

        graph_box = ctk.CTkFrame(
            right_panel,
            fg_color=COLORS["card"],
            corner_radius=8,
            border_width=1,
            border_color=COLORS["border"],
            height=260 if not self.is_compact else 205,
        )
        graph_box.pack(fill="x", pady=(0, 10))
        graph_box.pack_propagate(False)
    
        graph_header = ctk.CTkFrame(graph_box, fg_color="transparent")
        graph_header.pack(fill="x", padx=12 if self.is_compact else 18, pady=(10, 4))
        ctk.CTkLabel(
            graph_header,
            text=AppContext.t("Radar horario"),
            font=("Inter", 14 if self.is_compact else 18, "bold"),
            text_color=COLORS["text"],
        ).pack(side="left", anchor="w")

        self.fecha_var = ctk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))

        filtro_frame = ctk.CTkFrame(graph_header, fg_color="transparent")
        filtro_frame.pack(side="right", anchor="e")

        ctk.CTkLabel(
            filtro_frame,
            text=AppContext.t("Fecha"),
            text_color=COLORS["subtext"],
            font=("Inter", 11, "bold"),
        ).pack(side="left", padx=5)

        self.calendario = DateEntry(
            filtro_frame, width=12,
            background="#3B82F6", foreground="white",
            borderwidth=2, date_pattern="yyyy-mm-dd"
        )
        self.calendario.pack(side="left", padx=5)
        self.calendario.bind("<<DateEntrySelected>>", lambda e: self.filtrar_por_fecha())
        self.calendario.configure(font=("Inter", 10), justify="center")

        self.graph_container = ctk.CTkFrame(graph_box, fg_color="transparent")
        self.graph_container.pack(fill="both", expand=True, padx=8 if self.is_compact else 14, pady=(2, 8))

        self.filtrar_por_fecha()

        header_tabla = ctk.CTkFrame(right_panel, fg_color="transparent")
        header_tabla.pack(fill="x", pady=(0, 8))
        ctk.CTkLabel(
            header_tabla,
            text=AppContext.t("Actividad reciente"),
            font=("Inter", 14 if self.is_compact else 18, "bold"),
            text_color=COLORS["text"],
        ).pack(side="left", anchor="w")

        self.contenedor_tabla = ctk.CTkFrame(
            right_panel, fg_color=COLORS["card"],
            corner_radius=8, border_width=1, border_color=COLORS["border"]
        )
        self.contenedor_tabla.pack(fill="x", pady=(0, 24))
        self.render_mini_tabla_accesos_data()

    def filtrar_por_fecha(self):
        fecha = self.calendario.get_date().strftime("%Y-%m-%d")
        self.fecha_var.set(fecha)
        self.actualizar_grafica()

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
            SELECT CAST(strftime('%H', fecha_hora) AS INTEGER) AS hora, COUNT(*) AS total
            FROM registro_acceso
            WHERE DATE(fecha_hora) = ?
            GROUP BY hora ORDER BY hora
        """, (fecha,))
        filas = cursor.fetchall()
        conn.close()

        horas  = list(range(24))
        conteo = [0] * 24
        for fila in filas:
            conteo[int(fila[0])] = int(fila[1])

        mode       = ctk.get_appearance_mode()
        bg_color   = "#1E293B" if mode == "Dark" else "#FFFFFF"
        text_color = "#F8FAFC" if mode == "Dark" else "#0F172A"
        grid_color = "#334155" if mode == "Dark" else "#E2E8F0"
        line_color = "#3B82F6"

        fig = Figure(figsize=(7, 3.2), dpi=100)
        ax  = fig.add_subplot(111)

        fig.patch.set_facecolor(bg_color)
        ax.set_facecolor(bg_color)

        x = np.array(horas)
        y = np.array(conteo)

        if sum(conteo) > 0:
            x_smooth = np.linspace(x.min(), x.max(), 300)
            spl      = make_interp_spline(x, y, k=3)
            y_smooth = np.clip(spl(x_smooth), 0, None)
            ax.fill_between(x_smooth, y_smooth, color=line_color, alpha=0.22)
            ax.plot(x_smooth, y_smooth, color=line_color, linewidth=2.8)
            ax.scatter(x, y, s=28, color=line_color, edgecolors=bg_color, linewidths=1.2, zorder=3)
        else:
            ax.plot(horas, conteo, color=line_color, linewidth=2.5, alpha=0.6)
            ax.text(
                0.5, 0.5,
                AppContext.t("Sin accesos registrados en esta fecha"),
                transform=ax.transAxes, ha="center", va="center",
                fontsize=11, color=text_color, alpha=0.7
            )

        ax.set_xlim(0, 23)
        max_y = max(conteo) if conteo else 0
        ax.set_ylim(0, max(3, max_y + 1))
        ax.set_xticks([0, 3, 6, 9, 12, 15, 18, 21, 23])
        ax.set_xticklabels(
            ["00:00", "03:00", "06:00", "09:00", "12:00", "15:00", "18:00", "21:00", "23:00"],
            fontsize=9, color=text_color
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

        mode         = ctk.get_appearance_mode()
        bg_color     = "#1E293B" if mode == "Dark" else "#FFFFFF"
        row_color    = "#0F172A" if mode == "Dark" else "#F8FAFC"
        text_color   = "#F8FAFC" if mode == "Dark" else "#0F172A"
        subtext_color= "#CBD5E1" if mode == "Dark" else "#64748B"
        border_color = "#334155" if mode == "Dark" else "#E2E8F0"

        self.contenedor_tabla.configure(fg_color=bg_color, border_color=border_color)

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT r.id_registro, r.fecha_hora, r.resultado, r.motivo,
                   u.nombre, u.a_paterno, u.a_materno, u.cuenta, u.correo
            FROM registro_acceso r
            LEFT JOIN usuario u ON r.id_usuario = u.id_usuario
            ORDER BY r.fecha_hora DESC LIMIT 10
        """)
        registros = cursor.fetchall()
        conn.close()

        if not registros:
            ctk.CTkLabel(
                self.contenedor_tabla,
                text=AppContext.t("Sin accesos registrados"),
                font=("Inter", 13), text_color=subtext_color
            ).pack(pady=30)
            return

        for reg in registros:
            _, fecha_hora, resultado, motivo, nombre, ap, am, cuenta, correo = reg
            ok = int(resultado) == 1

            nombre_completo = (
                f"{nombre or ''} {ap or ''} {am or ''}".strip().upper()
                if nombre else AppContext.t("USUARIO NO REGISTRADO")
            )
            cuenta_txt = cuenta if cuenta else AppContext.t("Sin cuenta")
            correo_txt = correo if correo else AppContext.t("Sin correo")
            motivo_txt = motivo if motivo else (
                AppContext.t("Acceso autorizado") if ok else AppContext.t("Acceso denegado")
            )

            card = ctk.CTkFrame(
                self.contenedor_tabla, fg_color=row_color,
                corner_radius=12, border_width=1, border_color=border_color
            )
            card.pack(fill="x", padx=16, pady=8)

            top = ctk.CTkFrame(card, fg_color="transparent")
            top.pack(fill="x", padx=14, pady=(12, 4))

            ctk.CTkLabel(top, text="" if ok else "âŒ", font=("Inter", 22)).pack(side="left", padx=(0, 10))

            info = ctk.CTkFrame(top, fg_color="transparent")
            info.pack(side="left", fill="x", expand=True)

            ctk.CTkLabel(
                info, text=nombre_completo,
                font=("Inter", 13, "bold"), text_color=text_color, anchor="w"
            ).pack(anchor="w", fill="x")
            ctk.CTkLabel(
                info, text=f"ID: {cuenta_txt}  |  {correo_txt}",
                font=("Inter", 11), text_color=subtext_color, anchor="w"
            ).pack(anchor="w", fill="x")

            badge = ctk.CTkFrame(top, fg_color="#D1FAE5" if ok else "#FEE2E2", corner_radius=16)
            badge.pack(side="right")
            ctk.CTkLabel(
                badge,
                text=AppContext.t("AUTORIZADO") if ok else AppContext.t("DENEGADO"),
                font=("Inter", 9, "bold"),
                text_color="#065F46" if ok else "#991B1B"
            ).pack(padx=10, pady=4)

            bottom = ctk.CTkFrame(card, fg_color="transparent")
            bottom.pack(fill="x", padx=14, pady=(0, 12))
            ctk.CTkLabel(
                bottom, text=f"{fecha_hora}   |   {motivo_txt}",
                font=("Inter", 10), text_color=subtext_color, anchor="w"
            ).pack(anchor="w")
    def create_sidebar(self):
        self.sidebar_frame = ctk.CTkFrame(
            self, width=250 if not self.is_compact else 176, corner_radius=0,
            fg_color=COLORS["sidebar"],
            border_width=0
        )
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_propagate(False)

        header = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        header.pack(fill="x", pady=(15, 0), padx=15)
        ctk.CTkLabel(
            header, text="SECUREWORK",
            font=("Inter", 24 if not self.is_compact else 18, "bold"), text_color="#FFFFFF"
        ).pack(side="left", padx=10 if self.is_compact else 15)
        ctk.CTkFrame(self.sidebar_frame, fg_color=COLORS["accent"], height=3).pack(fill="x", padx=25, pady=(12, 0))

        if self.is_compact:
            ctk.CTkButton(
                header, text="X", width=26, height=26,
                fg_color="transparent", text_color=COLORS["sidebar_text"],
                hover_color="#1E293B", font=("Inter", 12, "bold"),
                command=self.cerrar_overlay
            ).pack(side="right", padx=(0, 5))

        if not self.is_compact:
            # -- Leer datos del perfil guardado --------------------------
            datos_perfil = _cargar_datos()

            profile = ctk.CTkFrame(self.sidebar_frame, fg_color="#111C31", corner_radius=8)
            profile.pack(pady=(28, 20), padx=16, fill="x")

            # Intentar cargar foto circular del perfil
            ruta_foto = datos_perfil.get("foto")
            ctk_img = None
            if ruta_foto and os.path.exists(ruta_foto):
                try:
                    from PIL import Image, ImageDraw
                    img = Image.open(ruta_foto).convert("RGBA")
                    lado = min(img.size)
                    img = img.crop((
                        (img.width - lado) // 2,
                        (img.height - lado) // 2,
                        (img.width + lado) // 2,
                        (img.height + lado) // 2,
                    ))
                    img = img.resize((46, 46), Image.LANCZOS)
                    mask = Image.new("L", (92, 92), 0)
                    ImageDraw.Draw(mask).ellipse((0, 0, 92, 92), fill=255)
                    mask = mask.resize((46, 46), Image.LANCZOS)
                    img.putalpha(mask)
                    ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(46, 46))
                except Exception:
                    ctk_img = None
            
            if ctk_img:
                # Guardar referencia para evitar garbage collection
                self._sidebar_ctk_img = ctk_img
                avatar_frame = ctk.CTkFrame(
                    profile, width=46, height=46,
                    corner_radius=23, fg_color="transparent"
                )
                avatar_frame.pack(side="left", padx=(12, 0), pady=12)
                avatar_frame.pack_propagate(False)
                ctk.CTkLabel(
                    avatar_frame, image=ctk_img, text="", fg_color="transparent"
                ).place(relx=0.5, rely=0.5, anchor="center")
            else:
                # Sin foto: mostrar emoji de persona
                ctk.CTkLabel(profile, text="", font=("Arial", 35)).pack(side="left", padx=(12, 0), pady=12)

            txt_info = ctk.CTkFrame(profile, fg_color="transparent")
            txt_info.pack(side="left", padx=10)

            # Nombre del perfil guardado
            ctk.CTkLabel(
                txt_info,
                text=datos_perfil.get("nombre", AppContext.t("ADMINISTRADOR")),
                font=("Inter", 14, "bold"),
                text_color=COLORS["sidebar_text"],
                wraplength=160,
                justify="left",
            ).pack(anchor="w")

            ctk.CTkLabel(
                txt_info, text=AppContext.t("Control BiomÃ©trico"),
                font=("Inter", 11), text_color=COLORS["sidebar_muted"]
            ).pack(anchor="w")

        self.btn_panel      = self.crear_btn_sidebar(self.sidebar_frame, AppContext.t("Inicio"),   self.mostrar_panel_control)
        self.btn_users      = self.crear_btn_sidebar(self.sidebar_frame, AppContext.t("Personal"), self.mostrar_gestion_usuarios)
        self.btn_areas      = self.crear_btn_sidebar(self.sidebar_frame, AppContext.t("Áreas"),    self.mostrar_gestion_areas)
        self.btn_puestos    = self.crear_btn_sidebar(self.sidebar_frame, AppContext.t("Puestos"),  self.mostrar_gestion_puestos)
        self.btn_account    = self.crear_btn_sidebar(self.sidebar_frame, AppContext.t("Ajustes"),  self.mostrar_cuenta)

        ctk.CTkButton(
            self.sidebar_frame,
            text=AppContext.t("Cerrar SesiÃ³n"),
            fg_color="transparent", text_color="#EF4444",
            hover_color="#33131B", font=("Inter", 14, "bold"), command=self.on_back
        ).pack(side="bottom", pady=30, padx=20, fill="x")

    def create_stat_card(self, master, title, value, color, index):
        card = ctk.CTkFrame(
            master, height=104, fg_color=COLORS["card"],
            corner_radius=8, border_width=1, border_color=COLORS["border"]
        )
        if self.is_compact:
            card.configure(height=72)
            row = index // 2
            col = index % 2
            card.grid(row=row, column=col, padx=6, pady=6, sticky="nsew")
        else:
            card.grid(row=0, column=index, padx=(0 if index == 0 else 12, 0), pady=0, sticky="nsew")

        ctk.CTkFrame(card, fg_color=color, height=4, corner_radius=0).pack(fill="x")
        ctk.CTkLabel(card, text=title, font=("Inter", 10 if self.is_compact else 12, "bold"), text_color=COLORS["subtext"]).pack(anchor="w", padx=12 if self.is_compact else 20, pady=(10 if self.is_compact else 15, 0))
        ctk.CTkLabel(card, text=value, font=("Inter", 24 if self.is_compact else 32, "bold"), text_color=COLORS["text"]).pack(anchor="w", padx=12 if self.is_compact else 20)

    def crear_btn_sidebar(self, master, texto, comando):
        command = comando
        if self.is_compact:
            command = lambda: [self.cerrar_overlay(), comando()]

        btn = ctk.CTkButton(
            master, text=texto, height=38 if self.is_compact else 44, anchor="w",
            fg_color="transparent", text_color=COLORS["sidebar_text"],
            hover_color="#1E293B", font=("Inter", 13 if self.is_compact else 15, "bold"),
            command=command
        )
        btn.pack(pady=3 if self.is_compact else 6, padx=10 if self.is_compact else 20, fill="x")
        return btn

    def create_top_controls(self, container):
        for widget in container.winfo_children():
            widget.destroy()

        shell = ctk.CTkFrame(container, fg_color=COLORS["sidebar"], corner_radius=0)
        shell.pack(fill="both", expand=True)

        ctk.CTkFrame(shell, fg_color=COLORS["accent"], height=3).pack(fill="x", side="top")

        def add_brand(parent, compact):
            brand = ctk.CTkFrame(parent, fg_color="transparent")
            brand.pack(side="left", padx=0, fill="y")
            ctk.CTkLabel(
                brand,
                text="SECUREWORK",
                font=("Inter", 17 if compact else 20, "bold"),
                text_color="#FFFFFF",
            ).pack(anchor="w")
            ctk.CTkLabel(
                brand,
                text=AppContext.t("Consola biometrica"),
                font=("Inter", 9 if compact else 11, "bold"),
                text_color=COLORS["sidebar_muted"],
            ).pack(anchor="w", pady=(2, 0))

        def add_controls(parent, compact):
            wrapper = ctk.CTkFrame(parent, fg_color="transparent")
            wrapper.pack(side="right", padx=0)
            datos_perfil = _cargar_datos()
            if not compact:
                profile = ctk.CTkFrame(wrapper, fg_color="#111C31", corner_radius=8, border_width=1, border_color="#22304A")
                profile.pack(side="left", padx=(0, 8))
                ctk.CTkLabel(
                    profile,
                    text=datos_perfil.get("nombre", AppContext.t("ADMINISTRADOR")).split(" ")[0].upper(),
                    font=("Inter", 11, "bold"),
                    text_color=COLORS["sidebar_text"],
                ).pack(padx=12, pady=(7, 0))
                ctk.CTkLabel(
                    profile,
                    text=datetime.now().strftime("%H:%M"),
                    font=("Inter", 15, "bold"),
                    text_color=COLORS["accent"],
                ).pack(padx=12, pady=(0, 7))

            t_f = ctk.CTkFrame(
                wrapper,
                fg_color="#111C31",
                corner_radius=8,
                width=62 if compact else 82,
                height=32,
                border_width=1,
                border_color="#22304A",
            )
            t_f.pack(side="left", padx=(0, 5))
            t_f.pack_propagate(False)
            self.theme_switch = ctk.CTkSwitch(
                t_f, text="", width=38,
                progress_color=COLORS["primary"], command=self.toggle_theme
            )
            if ctk.get_appearance_mode() == "Dark":
                self.theme_switch.select()
            else:
                self.theme_switch.deselect()
            self.theme_switch.place(relx=0.58, rely=0.5, anchor="center")

            l_c = ctk.CTkFrame(
                wrapper,
                fg_color="#111C31",
                corner_radius=8,
                width=96 if compact else 112,
                height=32,
                border_width=1,
                border_color="#22304A",
            )
            l_c.pack(side="left", padx=5)
            l_c.pack_propagate(False)

            color_es = COLORS["primary"] if AppContext.idioma_actual == "es" else "transparent"
            txt_es   = "white" if AppContext.idioma_actual == "es" else COLORS["sidebar_text"]
            color_en = COLORS["primary"] if AppContext.idioma_actual == "en" else "transparent"
            txt_en   = "white" if AppContext.idioma_actual == "en" else COLORS["sidebar_text"]
            btn_w = 41 if compact else 48

            ctk.CTkButton(
                l_c, text="ES", width=btn_w, height=24, corner_radius=6,
                fg_color=color_es, text_color=txt_es,
                command=lambda: self.cambiar_idioma_dashboard("es")
            ).pack(side="left", padx=(4, 2), pady=4)
            ctk.CTkButton(
                l_c, text="EN", width=btn_w, height=24, corner_radius=6,
                fg_color=color_en, text_color=txt_en,
                command=lambda: self.cambiar_idioma_dashboard("en")
            ).pack(side="left", padx=(2, 4), pady=4)

            ctk.CTkButton(
                wrapper,
                text=AppContext.t("Salir"),
                width=56 if compact else 70,
                height=32,
                corner_radius=8,
                fg_color="#33131B",
                hover_color="#4C1624",
                text_color="#FCA5A5",
                font=("Inter", 10 if compact else 12, "bold"),
                command=self.on_back,
            ).pack(side="left", padx=(5, 0))

        if self.is_compact:
            top_row = ctk.CTkFrame(shell, fg_color="transparent")
            top_row.pack(fill="x", padx=10, pady=(7, 4))
            add_brand(top_row, compact=True)
            add_controls(top_row, compact=True)

            nav_row = ctk.CTkFrame(shell, fg_color="transparent")
            nav_row.pack(fill="x", padx=6, pady=(0, 6))
            nav = ctk.CTkFrame(nav_row, fg_color="#0B1220", corner_radius=8)
            nav.pack(anchor="center")
        else:
            brand_host = ctk.CTkFrame(shell, fg_color="transparent")
            brand_host.pack(side="left", padx=18, pady=10, fill="y")
            add_brand(brand_host, compact=False)

            nav = ctk.CTkFrame(shell, fg_color="#0B1220", corner_radius=8)
            nav.pack(side="left", padx=10, pady=12)

            controls_host = ctk.CTkFrame(shell, fg_color="transparent")
            controls_host.pack(side="right", padx=10, pady=10)
            add_controls(controls_host, compact=False)

        self.btn_panel = self._crear_btn_topnav(nav, AppContext.t("Inicio"), self.mostrar_panel_control)
        self.btn_users = self._crear_btn_topnav(nav, AppContext.t("Personal"), self.mostrar_gestion_usuarios)
        self.btn_areas = self._crear_btn_topnav(nav, AppContext.t("Areas"), self.mostrar_gestion_areas)
        self.btn_puestos = self._crear_btn_topnav(nav, AppContext.t("Puestos"), self.mostrar_gestion_puestos)
        self.btn_account = self._crear_btn_topnav(nav, AppContext.t("Ajustes"), self.mostrar_cuenta)

        if hasattr(self, "vista_actual_func"):
            actual = {
                self.mostrar_panel_control: self.btn_panel,
                self.mostrar_gestion_usuarios: self.btn_users,
                self.mostrar_gestion_areas: self.btn_areas,
                self.mostrar_gestion_puestos: self.btn_puestos,
                self.mostrar_cuenta: self.btn_account,
            }.get(self.vista_actual_func)
            if actual:
                self.actualizar_navegacion(actual)

    def _crear_btn_topnav(self, master, texto, comando):
        btn = ctk.CTkButton(
            master,
            text=texto,
            width=58 if self.is_compact else 76,
            height=30,
            corner_radius=7,
            fg_color="#162033",
            hover_color="#22304A",
            text_color=COLORS["sidebar_text"],
            font=("Inter", 10 if self.is_compact else 12, "bold"),
            command=comando,
        )
        btn.pack(side="left", padx=3 if self.is_compact else 4, pady=4)
        return btn

    def cambiar_idioma_dashboard(self, nuevo_idioma):
        if AppContext.idioma_actual == nuevo_idioma:
            return
        AppContext.set_idioma(nuevo_idioma)
        self.refrescar_idioma_completo()

    def refrescar_idioma_completo(self):
        if hasattr(self, 'sidebar_frame') and self.sidebar_frame.winfo_exists():
            self.sidebar_frame.destroy()

        self.is_sidebar_open = False
        self._apply_shell_layout()

        self.create_top_controls(self.top_ctrl_area)

        if hasattr(self, 'vista_actual_func'):
            self.vista_actual_func()
