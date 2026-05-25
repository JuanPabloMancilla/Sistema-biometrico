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

        self.btn_panel      = None
        self.btn_users      = None
        self.btn_areas = None
        self.btn_puestos   = None
        self.btn_account    = None
        self.bind("<Configure>", self._on_resize)
        self.on_back = on_back

        # Referencia a imagen del sidebar para evitar garbage collection
        self._sidebar_ctk_img = None

        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.right_panel = ctk.CTkFrame(self, fg_color="transparent")
        self.right_panel.grid(row=0, column=1, sticky="nsew")

        self.top_ctrl_area = ctk.CTkFrame(self.right_panel, fg_color="transparent", height=70)
        self.top_ctrl_area.pack(side="top", fill="x")
        self.top_ctrl_area.pack_propagate(False)
        self.create_top_controls(self.top_ctrl_area)

        self.content_container = ctk.CTkFrame(self.right_panel, fg_color="transparent")
        self.content_container.pack(fill="both", expand=True)

        if not self.is_compact:
            self.create_sidebar()

        self.mostrar_panel_control()
    
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
        if hasattr(self, "overlay_sidebar") and self.overlay_sidebar.winfo_exists():
            self.overlay_sidebar.destroy()
            return

        self.overlay_sidebar = ctk.CTkFrame(
            self, width=280,
            fg_color=COLORS["sidebar"],
            border_width=1, border_color=COLORS["border"],
            corner_radius=0
        )
        self.overlay_sidebar.place(x=0, y=0, relheight=1)
        self.overlay_sidebar.lift()

        header = ctk.CTkFrame(self.overlay_sidebar, fg_color="transparent", height=75)
        header.pack(fill="x", padx=15, pady=(10, 5))
        header.pack_propagate(False)

        ctk.CTkLabel(
            header, text="SECUREWORK",
            font=("Inter", 22, "bold"), text_color=COLORS["primary"]
        ).pack(side="left", padx=(5, 0))

        ctk.CTkButton(
            header, text="", width=22, height=22,
            fg_color="transparent", text_color=COLORS["text"],
            hover_color=COLORS["hover"], font=("Inter", 14, "bold"),
            command=self.cerrar_overlay
        ).pack(side="right", padx=(0, 5), pady=5)

        self.construir_menu(self.overlay_sidebar)
    
    def crear_btn_overlay(self, master, texto, comando):
        ctk.CTkButton(
            master, text=texto, height=45, anchor="w",
            fg_color="transparent", text_color=COLORS["text"],
            hover_color=COLORS["hover"],
            command=lambda: [self.cerrar_overlay(), comando()]
        ).pack(fill="x", padx=20, pady=5)

    def cerrar_overlay(self):
        if hasattr(self, "overlay_sidebar") and self.overlay_sidebar.winfo_exists():
            self.overlay_sidebar.destroy()

    # -------------------------------------------------------------
    # RESIZE
    # -------------------------------------------------------------
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

        if not self.is_compact:
            self.create_sidebar()
        else:
            if hasattr(self, 'sidebar_frame') and self.sidebar_frame.winfo_exists():
                self.sidebar_frame.destroy()

        self.create_top_controls(self.top_ctrl_area)

        self.btn_panel      = None
        self.btn_users      = None
        self.btn_areas = None
        self.btn_puestos   = None
        self.btn_account    = None

        if hasattr(self, 'vista_actual_func') and self.vista_actual_func:
            self.after(50, self.vista_actual_func)
        else:
            self.after(50, self.mostrar_panel_control)
    
    def toggle_theme(self):
        if self.theme_switch.get() == 1:
            ctk.set_appearance_mode("dark")
        else:
            ctk.set_appearance_mode("light")
        self.refrescar_idioma_completo()

    def limpiar_derecha(self):
        for widget in self.content_container.winfo_children():
            widget.destroy()

    def actualizar_navegacion(self, btn_act):
        btns = [self.btn_panel, self.btn_users, self.btn_areas, self.btn_puestos, self.btn_account]
        for b in btns:
            if not b or not b.winfo_exists():
                continue
            if b == btn_act:
                b.configure(fg_color=COLORS["selected"], text_color=COLORS["primary"], hover_color=COLORS["selected"])
            else:
                b.configure(fg_color="transparent", text_color=COLORS["text"], hover_color=COLORS["hover"])

    # -------------------------------------------------------------
    # NAVEGACIï¿½N
    # -------------------------------------------------------------
    def mostrar_panel_control(self):
        self.vista_actual_func = self.mostrar_panel_control
        self.limpiar_derecha()
        if not self.is_compact:
            self.actualizar_navegacion(self.btn_panel)
        self.render_dashboard_principal()

    def mostrar_gestion_usuarios(self):
        self.vista_actual_func = self.mostrar_gestion_usuarios
        self.limpiar_derecha()
        if not self.is_compact:
            self.actualizar_navegacion(self.btn_users)
        UserManagementView(self.content_container).pack(fill="both", expand=True, padx=40)

    def mostrar_gestion_areas(self):
        self.vista_actual_func = self.mostrar_gestion_areas
        self.limpiar_derecha()
        if not self.is_compact:
            self.actualizar_navegacion(self.btn_areas)
        AreaManagementView(self.content_container).pack(fill="both", expand=True, padx=40)

    def mostrar_gestion_puestos(self):
        self.vista_actual_func = self.mostrar_gestion_puestos
        self.limpiar_derecha()
        if not self.is_compact:
            self.actualizar_navegacion(self.btn_puestos)
        PuestoManagementView(self.content_container).pack(fill="both", expand=True, padx=40)

    def mostrar_cuenta(self):
        self.vista_actual_func = self.mostrar_cuenta
        self.limpiar_derecha()
        if not self.is_compact:
            self.actualizar_navegacion(self.btn_account)
        AccountView(
            self.content_container,
            on_logout=self.on_back,
            on_profile_updated=self._refrescar_perfil_sidebar,  # ? NUEVO
        ).pack(fill="both", expand=True, padx=40)

    # -------------------------------------------------------------
    # ACTUALIZAR SIDEBAR CON PERFIL  ? NUEVO
    # -------------------------------------------------------------
    def _refrescar_perfil_sidebar(self):
        """Reconstruye el sidebar para mostrar nombre y foto actualizados."""
        if not self.is_compact:
            if hasattr(self, 'sidebar_frame') and self.sidebar_frame.winfo_exists():
                self.sidebar_frame.destroy()
            self.create_sidebar()
            # Restaurar resaltado del botï¿½n de cuenta
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
        padx_main = 15 if self.is_compact else 40

        main_scroll = ctk.CTkScrollableFrame(self.content_container, fg_color="transparent")
        main_scroll.pack(fill="both", expand=True)

        header = ctk.CTkFrame(main_scroll, fg_color="transparent")
        header.pack(fill="x", padx=padx_main, pady=(10, 20))
        ctk.CTkLabel(
            header,
            text=AppContext.t("Inicio"),
            font=("Inter", 30, "bold"), text_color=COLORS["text"]
        ).pack(anchor="w")
        ctk.CTkLabel(
            header,
            text=AppContext.t("Resumen operativo de accesos, personal y alertas"),
            font=("Inter", 16), text_color=COLORS["subtext"]
        ).pack(anchor="w")

        stats_frame = ctk.CTkFrame(main_scroll, fg_color="transparent")
        stats_frame.pack(fill="x", padx=padx_main, pady=10)
        if self.is_compact:
            stats_frame.grid_columnconfigure(0, weight=1)
            stats_frame.grid_columnconfigure(1, weight=1)

        total_registros, accesos_hoy, autorizados, denegados = self.obtener_estadisticas_dashboard()

        self.create_stat_card(stats_frame, AppContext.t("Personal activo"), str(total_registros), "#15803D", 0)
        self.create_stat_card(stats_frame, AppContext.t("Eventos de hoy"),  str(accesos_hoy),     "#2563EB", 1)
        self.create_stat_card(stats_frame, AppContext.t("Accesos validos"), str(autorizados),     "#0F766E", 2)
        self.create_stat_card(stats_frame, AppContext.t("Alertas"),         str(denegados),       "#DC2626", 3)

        graph_box = ctk.CTkFrame(
            main_scroll, fg_color=COLORS["card"],
            corner_radius=8, border_width=1, border_color=COLORS["border"], height=280
        )
        graph_box.pack(fill="x", padx=40, pady=20)
        graph_box.pack_propagate(False)
    
        ctk.CTkLabel(
            graph_box,
            text=AppContext.t("Tendencia de Accesos por Hora"),
            font=("Inter", 18, "bold"), text_color=COLORS["text"]
        ).pack(anchor="w", padx=30, pady=20)

        self.fecha_var = ctk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))

        filtro_frame = ctk.CTkFrame(graph_box, fg_color="transparent")
        filtro_frame.pack(anchor="w", padx=30, pady=(0, 10))

        ctk.CTkLabel(filtro_frame, text=AppContext.t("Fecha:")).pack(side="left", padx=5)

        self.calendario = DateEntry(
            filtro_frame, width=12,
            background="#3B82F6", foreground="white",
            borderwidth=2, date_pattern="yyyy-mm-dd"
        )
        self.calendario.pack(side="left", padx=5)
        self.calendario.bind("<<DateEntrySelected>>", lambda e: self.filtrar_por_fecha())
        self.calendario.configure(font=("Inter", 10), justify="center")

        self.graph_container = ctk.CTkFrame(graph_box, fg_color="transparent")
        self.graph_container.pack(fill="both", expand=True, padx=20, pady=10)

        self.filtrar_por_fecha()

        header_tabla = ctk.CTkFrame(main_scroll, fg_color="transparent")
        header_tabla.pack(fill="x", padx=75, pady=(20, 10))
        ctk.CTkLabel(
            header_tabla,
            text=AppContext.t("Registro de Ãºltimos accesos"),
            font=("Inter", 18, "bold"), text_color=COLORS["text"]
        ).pack(anchor="w")

        self.contenedor_tabla = ctk.CTkFrame(
            main_scroll, fg_color="white",
            corner_radius=8, border_width=1, border_color=COLORS["border"]
        )
        self.contenedor_tabla.pack(fill="x", padx=40, pady=(0, 40))
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
            self, width=250, corner_radius=0,
            fg_color=COLORS["sidebar"],
            border_width=1, border_color=COLORS["border"]
        )
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_propagate(False)

        header = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        header.pack(fill="x", pady=(15, 0), padx=15)
        ctk.CTkLabel(
            header, text="SECUREWORK",
            font=("Inter", 24, "bold"), text_color=COLORS["primary"]
        ).pack(side="left", padx=15)

        if not self.is_compact:
            # -- Leer datos del perfil guardado --------------------------
            datos_perfil = _cargar_datos()

            profile = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
            profile.pack(pady=(28, 20), padx=20, fill="x")

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
                avatar_frame.pack(side="left")
                avatar_frame.pack_propagate(False)
                ctk.CTkLabel(
                    avatar_frame, image=ctk_img, text="", fg_color="transparent"
                ).place(relx=0.5, rely=0.5, anchor="center")
            else:
                # Sin foto: mostrar emoji de persona
                ctk.CTkLabel(profile, text="", font=("Arial", 35)).pack(side="left")

            txt_info = ctk.CTkFrame(profile, fg_color="transparent")
            txt_info.pack(side="left", padx=10)

            # Nombre del perfil guardado
            ctk.CTkLabel(
                txt_info,
                text=datos_perfil.get("nombre", AppContext.t("ADMINISTRADOR")),
                font=("Inter", 14, "bold"),
                text_color=COLORS["text"],
                wraplength=160,
                justify="left",
            ).pack(anchor="w")

            ctk.CTkLabel(
                txt_info, text=AppContext.t("Control BiomÃ©trico"),
                font=("Inter", 11), text_color=COLORS["subtext"]
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
            font=("Inter", 14, "bold"), command=self.on_back
        ).pack(side="bottom", pady=30, padx=20, fill="x")

    def create_stat_card(self, master, title, value, color, index):
        card = ctk.CTkFrame(
            master, height=104, fg_color=COLORS["card"],
            corner_radius=8, border_width=1, border_color=COLORS["border"]
        )
        if self.is_compact:
            card.configure(height=80)
            row = index // 2
            col = index % 2
            card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
        else:
            card.pack(side="left", padx=(0, 20), expand=True, fill="both")

        ctk.CTkLabel(card, text=title, font=("Inter", 12, "bold"), text_color=COLORS["text"]).pack(anchor="w", padx=20, pady=(15, 0))
        ctk.CTkLabel(card, text=value, font=("Inter", 28, "bold"), text_color=color).pack(anchor="w", padx=20)

    def crear_btn_sidebar(self, master, texto, comando):
        btn = ctk.CTkButton(
            master, text=texto, height=44, anchor="w",
            fg_color="transparent", text_color=COLORS["text"],
            hover_color=COLORS["hover"], font=("Inter", 15, "bold"),
            command=comando
        )
        btn.pack(pady=6, padx=20, fill="x")
        return btn

    def create_top_controls(self, container):
        for widget in container.winfo_children():
            widget.destroy()

        if self.is_compact:
            ctk.CTkButton(
                container, text="", width=40, height=40,
                fg_color="transparent", text_color=COLORS["text"],
                command=self.toggle_sidebar_overlay
            ).pack(side="left", padx=20)

        wrapper = ctk.CTkFrame(container, fg_color="transparent")
        wrapper.pack(side="right", padx=40, pady=20)

        # Switch de Tema
        t_f = ctk.CTkFrame(wrapper, fg_color="#E8EEF5", corner_radius=8, width=100, height=38)
        t_f.pack(side="left", padx=10)
        t_f.pack_propagate(False)
        ctk.CTkLabel(t_f, text="", font=("Inter", 16)).place(x=20, y=19, anchor="center")
        self.theme_switch = ctk.CTkSwitch(
            t_f, text="", width=40,
            progress_color=COLORS["primary"], command=self.toggle_theme
        )
        if ctk.get_appearance_mode() == "Dark":
            self.theme_switch.select()
        else:
            self.theme_switch.deselect()
        self.theme_switch.place(x=65, y=19, anchor="center")

        # Selector de Idioma
        l_c = ctk.CTkFrame(wrapper, fg_color="#E8EEF5", corner_radius=8, height=38)
        l_c.pack(side="left", padx=10)
        ctk.CTkLabel(l_c, text="", font=("Inter", 16)).pack(side="left", padx=(12, 5))

        color_es = COLORS["primary"] if AppContext.idioma_actual == "es" else "transparent"
        txt_es   = "white"   if AppContext.idioma_actual == "es" else COLORS["text"]
        color_en = COLORS["primary"] if AppContext.idioma_actual == "en" else "transparent"
        txt_en   = "white"   if AppContext.idioma_actual == "en" else COLORS["text"]

        ctk.CTkButton(
            l_c, text="ES", width=38, height=28, corner_radius=6,
            fg_color=color_es, text_color=txt_es,
            command=lambda: self.cambiar_idioma_dashboard("es")
        ).pack(side="left", padx=2, pady=5)
        ctk.CTkButton(
            l_c, text="EN", width=38, height=28, corner_radius=6,
            fg_color=color_en, text_color=txt_en,
            command=lambda: self.cambiar_idioma_dashboard("en")
        ).pack(side="left", padx=(2, 10), pady=5)

    def cambiar_idioma_dashboard(self, nuevo_idioma):
        if AppContext.idioma_actual == nuevo_idioma:
            return
        AppContext.set_idioma(nuevo_idioma)
        self.refrescar_idioma_completo()

    def refrescar_idioma_completo(self):
        if hasattr(self, 'sidebar_frame') and self.sidebar_frame.winfo_exists():
            self.sidebar_frame.destroy()

        if not self.is_compact:
            self.create_sidebar()

        self.create_top_controls(self.top_ctrl_area)

        if self.is_compact:
            self.btn_panel      = None
            self.btn_users      = None
            self.btn_areas = None
            self.btn_puestos   = None
            self.btn_account    = None

        if hasattr(self, 'vista_actual_func'):
            self.vista_actual_func()
