import customtkinter as ctk
import re
from app.views.terminal_view import TerminalView
from app.services.theme import COLORS
from app.views.app_context import AppContext
from app.detection.detector_rostro import encodings_db, usuarios_db
from app.recognition.encoding_manager import (
    cargar_encodings,
    eliminar_encoding,
    guardar_encoding,
    find_best_match
)
from app.services.puesto_service import obtener_todas_carreras, obtener_facultades_para_dropdown, obtener_id_carrera_por_nombre
from app.services.usuario_service import (
    crear_usuario,
    actualizar_usuario,
    existe_correo,
    existe_cuenta,
    obtener_todos_usuarios,
    obtener_usuario_por_id,
    obtener_id_facultad_por_nombre,
    desactivar_usuario,
    reactivar_usuario
)

TIPOS_USUARIO = {
    1: "Trabajador",
    2: "Supervisor",
    3: "Administrativo"
}

class UserManagementView(ctk.CTkFrame):
    def __init__(self, master, controller=None):
        super().__init__(master, fg_color=COLORS["bg"])
        self.controller = controller
        self.usuario_editando_id = None

        self.font_header = ("Inter", 28, "bold")
        self.font_sub    = ("Inter", 14, "bold")
        self.font_normal = ("Inter", 12)
        self.font_small  = ("Inter", 12, "bold")

        self.rol_var             = ctk.StringVar(value="TRABAJADOR")
        self.carrera_var         = ctk.StringVar()
        self.inputs_obligatorios = {}
        self.inputs_apellidos    = {}

        self.refresh_data()

        self.colors = {
            "SUPERVISOR":      {"bg": "#E0F2FE", "text": "#0369A1"},
            "TRABAJADOR":      {"bg": "#D1FAE5", "text": "#047857"},
            "ADMINISTRATIVO":  {"bg": "#F3E8FF", "text": "#7E22CE"}
        }

        self.filtro_rol_actual = "Todos"
        self.filter_visible    = False
        self.is_compact        = False
        self.bind("<Configure>", self._on_resize)

        self.vista_tabla = ctk.CTkFrame(self, fg_color="transparent")
        self.vista_tabla.pack(fill="both", expand=True)

        self.create_header(self.vista_tabla)
        self.create_search_bar(self.vista_tabla)

        self.filter_container = ctk.CTkFrame(self.vista_tabla, fg_color="transparent")

        self.main_card = ctk.CTkFrame(
            self.vista_tabla,
            fg_color=COLORS["card"],
            corner_radius=8,
            border_width=1,
            border_color=COLORS["border"]
        )
        self.main_card.pack(expand=True, fill="both", padx=20, pady=(5, 10))

        self.render_table_content(self.all_users)

    def refresh_data(self):
        try:
            data = obtener_todos_usuarios()
            self.all_users = []
            for u in data:
                self.all_users.append({
                    "nombre_solo": u["nombre"],
                    "ap":          u["a_paterno"],
                    "am":          u["a_materno"],
                    "r":           TIPOS_USUARIO.get(u.get("tipo_usuario", 1), "N/A"),
                    "cuenta":      u.get("cuenta", ""),
                    "id":          u["id_usuario"],
                    "correo":      u.get("correo", ""),
                    "estado":      u.get("estado", 1),
                    "facultad": u.get("facultad_nombre", ""),
                    "carrera": u.get("carrera_nombre", "")
                })
            self.all_users.sort(key=lambda u: (u["estado"] == 0, u["nombre_solo"]))
        except Exception as e:
            print("Error usuarios:", e)
            self.all_users = []

    # -------------------------------------------------------------
    # HELPERS
    # -------------------------------------------------------------
    def validar_ocho_numeros(self, P):
        if P == "":
            return True
        return P.isdigit() and len(P) <= 8

    def limpiar_texto(self, texto):
        return " ".join(texto.strip().split()).title()

    def validar_texto_real(self, texto):
        texto = texto.strip()
        if len(texto) < 2:
            return False
        return bool(re.match(r"^[A-Za-zÃÃ‰ÃÃ“ÃšÃ¡Ã©Ã­Ã³ÃºÃ‘Ã±\s]+$", texto))

    def _on_resize(self, event):
        nuevo_compact = event.width < 1040
        if nuevo_compact != self.is_compact:
            self.is_compact = nuevo_compact
            if hasattr(self, "vista_tabla") and self.vista_tabla.winfo_exists():
                for w in self.vista_tabla.winfo_children():
                    w.destroy()
                self.create_header(self.vista_tabla)
                self.create_search_bar(self.vista_tabla)
                self.filter_container = ctk.CTkFrame(self.vista_tabla, fg_color="transparent")
                self.main_card = ctk.CTkFrame(
                    self.vista_tabla,
                    fg_color=COLORS["card"],
                    corner_radius=8,
                    border_width=1,
                    border_color=COLORS["border"]
                )
                self.main_card.pack(
                    expand=True, fill="both",
                    padx=8 if self.is_compact else 30,
                    pady=(5, 15)
                )
                self.render_table_content(self.all_users)

    # -------------------------------------------------------------
    # TABLA
    # -------------------------------------------------------------
    def render_table_content(self, user_list):
        for w in self.main_card.winfo_children():
            w.destroy()

        scroll = ctk.CTkScrollableFrame(
            self.main_card,
            fg_color=COLORS["card"],
            scrollbar_button_color="#CBD5E1",
            scrollbar_button_hover_color="#94A3B8",
        )
        scroll.pack(expand=True, fill="both", padx=8 if self.is_compact else 20, pady=10)

        if not user_list:
            ctk.CTkLabel(
                scroll,
                text=AppContext.t("No hay usuarios registrados"),
                font=self.font_normal,
                text_color=COLORS["subtext"]
            ).pack(pady=40)
            return

        # -- VISTA COMPACTA --------------------------------------
        if self.is_compact:
            for u in user_list:
                es_activo = u.get("estado", 1) == 1

                card = ctk.CTkFrame(
                    scroll, fg_color=COLORS["card"],
                    corner_radius=8, border_width=1, border_color=COLORS["border"]
                )
                card.pack(fill="x", padx=2, pady=5)

                top = ctk.CTkFrame(card, fg_color="transparent")
                top.pack(fill="x", padx=10, pady=(8, 3))

                ctk.CTkLabel(top, text="", font=("Inter", 28)).pack(side="left", padx=(0, 8))

                info = ctk.CTkFrame(top, fg_color="transparent")
                info.pack(side="left", fill="x", expand=True)

                wrap = max(180, min(520, max(self.winfo_width(), 520) - 150))

                ctk.CTkLabel(
                    info,
                    text=f"{u['nombre_solo']} {u['ap']} {u['am']}".upper(),
                    font=("Inter", 12, "bold"), text_color=COLORS["text"],
                    anchor="w", wraplength=wrap, justify="left"
                ).pack(anchor="w", fill="x")

                ctk.CTkLabel(
                    info, text=f"ID: {u['cuenta']}",
                    font=("Inter", 11), text_color=COLORS["subtext"], anchor="w"
                ).pack(anchor="w", fill="x")

                if u["correo"]:
                    ctk.CTkLabel(
                        info, text=u["correo"],
                        font=("Inter", 10), text_color=COLORS["subtext"],
                        anchor="w", wraplength=wrap, justify="left"
                    ).pack(anchor="w", fill="x")

                area = u.get("facultad") or AppContext.t("Sin área")
                puesto = u.get("carrera") or AppContext.t("Sin puesto")
                ctk.CTkLabel(
                    info,
                    text=f"{AppContext.t('Área')}: {area}",
                    font=("Inter", 10), text_color=COLORS["subtext"],
                    anchor="w", wraplength=wrap, justify="left"
                ).pack(anchor="w", fill="x", pady=(2, 0))
                ctk.CTkLabel(
                    info,
                    text=f"{AppContext.t('Puesto')}: {puesto}",
                    font=("Inter", 10), text_color=COLORS["subtext"],
                    anchor="w", wraplength=wrap, justify="left"
                ).pack(anchor="w", fill="x")

                badges = ctk.CTkFrame(card, fg_color="transparent")
                badges.pack(fill="x", padx=12, pady=(4, 8))

                col = self.colors.get(u["r"].upper(), {"bg": "#E2E8F0", "text": "#475569"})
                badge_r = ctk.CTkFrame(badges, fg_color=col["bg"], corner_radius=8)
                badge_r.pack(side="left", padx=(0, 6))
                ctk.CTkLabel(
                    badge_r,
                    text=AppContext.t(u["r"]),
                    font=("Inter", 9, "bold"),
                    text_color=col["text"]
                ).pack(padx=8, pady=3)

                badge_e = ctk.CTkFrame(
                    badges,
                    fg_color="#D1FAE5" if es_activo else "#FEE2E2",
                    corner_radius=8
                )
                badge_e.pack(side="left")
                ctk.CTkLabel(
                    badge_e,
                    text="" + (AppContext.t("ACTIVO") if es_activo else AppContext.t("INACTIVO")),
                    font=("Inter", 9, "bold"),
                    text_color="#065F46" if es_activo else "#991B1B"
                ).pack(padx=8, pady=3)

                actions = ctk.CTkFrame(card, fg_color="transparent")
                actions.pack(fill="x", padx=10, pady=(0, 8))

                ctk.CTkButton(
                    actions,
                    text="✎",
                    width=42, height=30,
                    fg_color=COLORS["hover"], text_color=COLORS["text"],
                    font=("Segoe UI Symbol", 14, "bold"),
                    command=lambda d=u: self.abrir_formulario(d)
                ).pack(side="left", padx=(0, 6))

                if es_activo:
                    ctk.CTkButton(
                        actions,
                        text="⊘",
                        width=42, height=30,
                        fg_color="#FFF1F2", text_color="#E11D48",
                        font=("Segoe UI Symbol", 14, "bold"),
                        command=lambda i=u["id"], n=f"{u['nombre_solo']} {u['ap']}": self.confirmar_cambio_estado(i, n, desactivar=True)
                    ).pack(side="left", padx=(6, 0))
                else:
                    ctk.CTkButton(
                        actions,
                        text="✓",
                        width=42, height=30,
                        fg_color="#10B981", text_color="white",
                        font=("Segoe UI Symbol", 14, "bold"),
                        command=lambda i=u["id"], n=f"{u['nombre_solo']} {u['ap']}": self.confirmar_cambio_estado(i, n, desactivar=False)
                    ).pack(side="left", padx=(6, 0))

        # -- VISTA ESCRITORIO ------------------------------------
        else:
            for u in user_list:
                es_activo = u.get("estado", 1) == 1
                nombre_completo = f"{u['nombre_solo']} {u['ap']} {u['am']}".strip()
                iniciales = "".join([
                    parte[:1] for parte in nombre_completo.split()
                    if parte
                ][:2]).upper() or "P"

                card = ctk.CTkFrame(
                    scroll,
                    fg_color=COLORS["card"],
                    corner_radius=8,
                    border_width=1,
                    border_color=COLORS["border"],
                    height=112
                )
                card.pack(fill="x", side="top", pady=8, padx=4)
                card.pack_propagate(False)

                ctk.CTkFrame(
                    card,
                    fg_color=COLORS["primary"] if es_activo else "#DC2626",
                    width=5,
                    corner_radius=0
                ).pack(side="left", fill="y")

                avatar = ctk.CTkFrame(card, fg_color=COLORS["hover"], width=54, height=54, corner_radius=27)
                avatar.pack(side="left", padx=(18, 16))
                avatar.pack_propagate(False)
                ctk.CTkLabel(
                    avatar,
                    text=iniciales,
                    font=("Inter", 16, "bold"),
                    text_color=COLORS["text"]
                ).place(relx=0.5, rely=0.5, anchor="center")

                info = ctk.CTkFrame(card, fg_color="transparent")
                info.pack(side="left", fill="both", expand=True, pady=16)

                ctk.CTkLabel(
                    info,
                    text=nombre_completo.upper(),
                    font=("Inter", 14, "bold"),
                    text_color=COLORS["text"],
                    anchor="w"
                ).pack(anchor="w", fill="x")

                col = self.colors.get(u["r"].upper(), {"bg": "#E2E8F0", "text": "#475569"})
                ctk.CTkLabel(
                    info,
                    text=f"ID: {u['cuenta']}  |  {u['correo']}",
                    font=("Inter", 11),
                    text_color=COLORS["subtext"],
                    anchor="w"
                ).pack(anchor="w")

                area = u.get("facultad") or AppContext.t("Sin área")
                puesto = u.get("carrera") or AppContext.t("Sin puesto")
                ctk.CTkLabel(
                    info,
                    text=f"{AppContext.t('Área')}: {area}  |  {AppContext.t('Puesto')}: {puesto}",
                    font=("Inter", 11),
                    text_color=COLORS["subtext"],
                    anchor="w"
                ).pack(anchor="w", pady=(3, 0))

                badges = ctk.CTkFrame(info, fg_color="transparent")
                badges.pack(anchor="w", pady=(8, 0))

                badge_r = ctk.CTkFrame(badges, fg_color=col["bg"], corner_radius=8)
                badge_r.pack(side="left", padx=(0, 8))
                ctk.CTkLabel(
                    badge_r,
                    text=AppContext.t(u["r"]),
                    font=("Inter", 9, "bold"),
                    text_color=col["text"]
                ).pack(padx=9, pady=3)

                badge_e = ctk.CTkFrame(badges, fg_color="#D1FAE5" if es_activo else "#FEE2E2", corner_radius=8)
                badge_e.pack(side="left")
                ctk.CTkLabel(
                    badge_e,
                    text="" + (AppContext.t("ACTIVO") if es_activo else AppContext.t("INACTIVO")),
                    font=("Inter", 9, "bold"),
                    text_color="#065F46" if es_activo else "#991B1B"
                ).pack(padx=9, pady=3)

                a_b = ctk.CTkFrame(card, fg_color="transparent")
                a_b.pack(side="right", padx=22)

                ctk.CTkButton(
                    a_b, text="✎",
                    width=38, height=34,
                    fg_color="#E8F7EF", hover_color="#D1FAE5",
                    text_color=COLORS["primary"],
                    font=("Segoe UI Symbol", 14, "bold"),
                    command=lambda d=u: self.abrir_formulario(d)
                ).pack(side="left", padx=4)

                if es_activo:
                    ctk.CTkButton(
                        a_b, text="⊘",
                        width=38, height=34,
                        fg_color="#FFF1F2", hover_color="#FFE4E6",
                        text_color="#E11D48",
                        font=("Segoe UI Symbol", 14, "bold"),
                        command=lambda i=u["id"], n=f"{u['nombre_solo']} {u['ap']}": self.confirmar_cambio_estado(i, n, desactivar=True)
                    ).pack(side="left", padx=2)
                else:
                    ctk.CTkButton(
                        a_b, text="✓",
                        width=38, height=34,
                        fg_color="#10B981", text_color="white",
                        font=("Segoe UI Symbol", 14, "bold"),
                        hover_color="#059669",
                        command=lambda i=u["id"], n=f"{u['nombre_solo']} {u['ap']}": self.confirmar_cambio_estado(i, n, desactivar=False)
                    ).pack(side="left", padx=2)

    def confirmar_cambio_estado(self, id_usuario, nombre, desactivar=True):
        self.overlay = ctk.CTkFrame(self, fg_color="transparent")
        self.overlay.place(relx=0, rely=0, relwidth=1, relheight=1)

        modal = ctk.CTkFrame(
            self.overlay, fg_color=COLORS["card"], corner_radius=8,
            width=340 if self.is_compact else 420,
            height=220 if self.is_compact else 250,
            border_width=2, border_color="#CBD5E1"
        )
        modal.place(relx=0.5, rely=0.5, anchor="center")
        modal.pack_propagate(False)

        if desactivar:
            icono     = ""
            titulo    = AppContext.t("Â¿Desactivar este usuario?")
            sub       = AppContext.t("El usuario perderÃ¡ acceso al sistema.")
            btn_txt   = AppContext.t("Desactivar")
            btn_color = "#EF4444"
            btn_hover = "#DC2626"
        else:
            icono     = ""
            titulo    = AppContext.t("Â¿Activar este usuario?")
            sub       = AppContext.t("El usuario recuperarÃ¡ acceso al sistema.")
            btn_txt   = AppContext.t("Activar")
            btn_color = "#10B981"
            btn_hover = "#059669"

        ctk.CTkLabel(modal, text=icono, font=("Inter", 32 if self.is_compact else 45)).pack(pady=(12 if self.is_compact else 20, 5))
        ctk.CTkLabel(modal, text=titulo, font=("Inter", 14 if self.is_compact else 16, "bold"), text_color=COLORS["text"]).pack()
        ctk.CTkLabel(modal, text=nombre.upper(), font=("Inter", 12, "bold"), text_color=COLORS["subtext"]).pack()
        ctk.CTkLabel(modal, text=sub, font=("Inter", 11), text_color=COLORS["subtext"]).pack(pady=(2, 0))

        btns = ctk.CTkFrame(modal, fg_color="transparent")
        btns.pack(fill="x", side="bottom", pady=25, padx=30)

        ctk.CTkButton(
            btns, text=AppContext.t("Cancelar"),
            fg_color="#94A3B8", text_color="white", hover_color="#64748B",
            height=40, font=("Inter", 13, "bold"),
            command=self.cerrar_modal
        ).pack(side="left", expand=True, padx=(0, 10))

        ctk.CTkButton(
            btns, text=btn_txt,
            fg_color=btn_color, text_color="white", hover_color=btn_hover,
            height=40, font=("Inter", 13, "bold"),
            command=lambda: self._ejecutar_cambio_estado(id_usuario, desactivar)
        ).pack(side="left", expand=True)

    def _ejecutar_cambio_estado(self, id_usuario, desactivar_flag):
        if desactivar_flag:
            desactivar_usuario(id_usuario)
        else:
            reactivar_usuario(id_usuario)
        self.refresh_data()
        self.render_table_content(self.all_users)
        self.cerrar_modal()

    def cerrar_modal(self):
        if hasattr(self, "overlay"):
            self.overlay.destroy()

    def abrir_formulario(self, usuario=None):
        self.vista_tabla.pack_forget()
        self.inputs_obligatorios, self.inputs_apellidos = {}, {}

        if not usuario:
            self.biometria_temp = None

        self.usuario_editando_id = usuario["id"] if usuario else None
        self.rol_var.set(usuario["r"].upper() if usuario else "TRABAJADOR")

        self.estado_var = ctk.BooleanVar(value=True)
        if usuario:
            self.estado_var.set(usuario.get("estado", 1) == 1)

        self.dict_facultades = obtener_facultades_para_dropdown()
        nombres_f = list(self.dict_facultades.values()) if self.dict_facultades else ["Sin Datos"]
        self.carreras_por_plantel = {}

        for c in obtener_todas_carreras():
            if c.get("estado", 1) != 1:
                continue
            fn = c["facultad_nombre"]
            if fn not in self.carreras_por_plantel:
                self.carreras_por_plantel[fn] = []
            self.carreras_por_plantel[fn].append(c["nombre"])

        self.form_base = ctk.CTkFrame(self, fg_color=COLORS["bg"])
        self.form_base.pack(fill="both", expand=True)

        padx_form = 8 if self.is_compact else 36
        self.form_actions = ctk.CTkFrame(
            self.form_base,
            fg_color=COLORS["card"],
            corner_radius=8,
            border_width=1,
            border_color=COLORS["border"],
        )
        self.form_actions.pack(
            side="bottom",
            fill="x",
            padx=padx_form,
            pady=(4, 8),
        )

        self.form_container = ctk.CTkScrollableFrame(self.form_base, fg_color="transparent")
        self.form_container.pack(fill="both", expand=True, padx=padx_form, pady=10)

        ctk.CTkLabel(
            self.form_container,
            text=(AppContext.t("Editar Registro")) if usuario else (AppContext.t("Nuevo Registro")),
            font=("Inter", 20, "bold") if self.is_compact else self.font_header, text_color=COLORS["text"]
        ).pack(anchor="w", padx=0, pady=(6 if self.is_compact else 24, 5))

        c_clasi = ctk.CTkFrame(
            self.form_container, fg_color=COLORS["card"],
            corner_radius=8, border_width=1, border_color=COLORS["border"]
        )
        c_clasi.pack(fill="x", padx=0, pady=6)

        ctk.CTkLabel(
            c_clasi,
            text=AppContext.t("ClasificaciÃ³n"),
            font=self.font_sub,
            text_color=COLORS["text"]
        ).pack(anchor="w", padx=14, pady=(10, 3))

        grid = ctk.CTkFrame(c_clasi, fg_color="transparent")
        grid.pack(fill="x", padx=14, pady=(0, 10))

        def crear_campo_menu(titulo):
            campo = ctk.CTkFrame(grid, fg_color="transparent")
            if self.is_compact:
                campo.pack(fill="x", pady=3)
            else:
                campo.pack(side="left", expand=True, fill="x", padx=5)
            ctk.CTkLabel(
                campo,
                text=titulo,
                font=self.font_small,
                text_color=COLORS["subtext"]
            ).pack(anchor="w")
            return campo

        campo_rol = crear_campo_menu(AppContext.t("Tipo de Usuario"))
        self.rol_menu = ctk.CTkOptionMenu(
            campo_rol,
            values=["TRABAJADOR", "SUPERVISOR", "ADMINISTRATIVO"],
            variable=self.rol_var,
            height=34 if self.is_compact else 38,
            text_color=COLORS["text"],
            fg_color=COLORS["hover"],
            button_color=COLORS["border"]
        )
        self.rol_menu.pack(fill="x", pady=(5, 0))

        campo_facultad = crear_campo_menu(AppContext.t("Facultad"))
        self.plantel_menu = ctk.CTkOptionMenu(
            campo_facultad,
            values=nombres_f,
            command=self.update_carreras_dinamicas,
            height=34 if self.is_compact else 38,
            text_color=COLORS["text"],
            fg_color=COLORS["hover"],
            button_color=COLORS["border"]
        )
        self.plantel_menu.pack(fill="x", pady=(5, 0))

        campo_carrera = crear_campo_menu(AppContext.t("Carrera"))
        self.carrera_menu = ctk.CTkOptionMenu(
            campo_carrera,
            variable=self.carrera_var,
            values=[],
            height=34 if self.is_compact else 38,
            text_color=COLORS["text"],
            fg_color=COLORS["hover"],
            button_color=COLORS["border"]
        )
        self.carrera_menu.pack(fill="x", pady=(5, 0))

        if usuario:
            facultad_actual = usuario.get("facultad", "")
            carrera_actual = usuario.get("carrera", "")

            if facultad_actual in nombres_f:
                self.plantel_menu.set(facultad_actual)
                self.update_carreras_dinamicas(facultad_actual)

                carreras_disponibles = self.carreras_por_plantel.get(facultad_actual, [])

                if carrera_actual in carreras_disponibles:
                    self.carrera_var.set(carrera_actual)
            else:
                self.update_carreras_dinamicas(nombres_f[0])

        else:
            if nombres_f:
                self.update_carreras_dinamicas(nombres_f[0])

        self.create_section_card(self.form_container, AppContext.t("InformaciÃ³n Personal"), [
            ("Nombres",          usuario["nombre_solo"] if usuario else ""),
            ("Apellido Paterno", usuario["ap"]          if usuario else ""),
            ("Apellido Materno", usuario["am"]          if usuario else "")
        ])
        self.create_section_card(self.form_container, AppContext.t("IdentificaciÃ³n"), [
            ("cuenta", str(usuario["cuenta"]) if usuario and usuario["cuenta"] else ""),
            ("correo", str(usuario["correo"]) if usuario and usuario["correo"] else "")
        ])

        if usuario:
            estado_card = ctk.CTkFrame(
                self.form_container, fg_color=COLORS["card"],
                corner_radius=8, border_width=1, border_color=COLORS["border"]
            )
            estado_card.pack(fill="x", padx=0, pady=10)
            ctk.CTkLabel(
                estado_card,
                text=AppContext.t("Estado del usuario"),
                font=self.font_sub, text_color=COLORS["text"]
            ).pack(anchor="w", padx=20, pady=(15, 5))
            self.switch_estado = ctk.CTkSwitch(
                estado_card,
                text=AppContext.t("Usuario activo"),
                variable=self.estado_var,
                onvalue=True, offvalue=False,
                font=self.font_normal, text_color=COLORS["text"]
            )
            self.switch_estado.pack(anchor="w", padx=20, pady=(5, 20))

        vcmd = (self.register(self.validar_ocho_numeros), "%P")
        entrada = self.inputs_obligatorios.get("cuenta")
        if entrada:
            entrada.configure(validate="key", validatecommand=vcmd)

        self.btn_biometria = ctk.CTkButton(
            self.form_actions,
            text=AppContext.t("Registrar BiometrÃ­a"),
            height=36 if self.is_compact else 42,
            fg_color="#0EA5E9", text_color="white",
            font=self.font_sub, command=self.abrir_terminal_biometrica
        )
        self.btn_biometria.pack(fill="x", padx=8, pady=(7, 3))

        self.label_estado = ctk.CTkLabel(
            self.form_actions, text="",
            font=self.font_small, text_color="#EF4444"
        )
        self.label_estado.pack(fill="x", padx=10, pady=0)

        btns = ctk.CTkFrame(self.form_actions, fg_color="transparent")
        btns.pack(fill="x", padx=8, pady=(3, 7))

        self.btn_guardar = ctk.CTkButton(
            btns,
            text=AppContext.t("Guardar Usuario"),
            font=self.font_sub,
            fg_color="#D1FAE5",
            text_color="#065F46",
            hover_color="#BBF7D0",
            corner_radius=8,
            height=36 if self.is_compact else 42,
            command=self.validar_y_guardar
        )
        btn_cancelar = ctk.CTkButton(
            btns,
            text=AppContext.t("Cancelar"),
            font=self.font_sub,
            fg_color="#FEE2E2",
            text_color="#991B1B",
            hover_color="#FECACA",
            corner_radius=8,
            height=36 if self.is_compact else 42,
            command=self.cerrar_formulario
        )

        ancho_actual = self.winfo_width()
        if ancho_actual <= 1 and self.master:
            ancho_actual = self.master.winfo_width()
        if ancho_actual <= 1:
            ancho_actual = self.winfo_toplevel().winfo_width()
        apilar_botones = self.is_compact and 1 < ancho_actual < 520

        if apilar_botones:
            btn_cancelar.pack(fill="x", pady=(0, 10))
            self.btn_guardar.pack(fill="x")
        else:
            btn_cancelar.pack(side="left", expand=True, fill="x", padx=(0, 10))
            self.btn_guardar.pack(side="left", expand=True, fill="x", padx=(10, 0))

    def create_section_card(self, master, title, fields):
        card = ctk.CTkFrame(
            master, fg_color=COLORS["card"],
            corner_radius=8, border_width=1, border_color=COLORS["border"]
        )
        card.pack(fill="x", padx=0, pady=6)
        ctk.CTkLabel(card, text=title, font=self.font_sub, text_color=COLORS["text"]).pack(anchor="w", padx=14, pady=(10, 3))
        grid = ctk.CTkFrame(card, fg_color="transparent")
        grid.pack(fill="x", padx=14, pady=(0, 10))
        for label, val in fields:
            f = ctk.CTkFrame(grid, fg_color="transparent")
            if self.is_compact:
                f.pack(fill="x", pady=3)
            else:
                f.pack(side="left", expand=True, fill="x", padx=5)
            ctk.CTkLabel(
                f,
                text=AppContext.t(label),
                font=self.font_small, text_color=COLORS["subtext"]
            ).pack(anchor="w")
            entry = ctk.CTkEntry(
                f, height=34 if self.is_compact else 38, font=self.font_normal,
                fg_color=COLORS["hover"], border_width=0, text_color=COLORS["text"]
            )
            entry.insert(0, val)
            entry.pack(fill="x", pady=5)
            if "Apellido" in label:
                self.inputs_apellidos[label] = entry
            else:
                self.inputs_obligatorios[label] = entry

    def _limpiar_errores(self):
        for entry in self.inputs_obligatorios.values():
            entry.configure(border_width=0)
        for entry in self.inputs_apellidos.values():
            entry.configure(border_width=0)
        if hasattr(self, "label_estado"):
            self.label_estado.configure(text="")

    def _mostrar_error(self, campo, mensaje):
        entry = self.inputs_obligatorios.get(campo) or self.inputs_apellidos.get(campo)
        if entry:
            entry.configure(border_width=2, border_color="#EF4444")
        if hasattr(self, "label_estado"):
            self.label_estado.configure(text=f"Error: {mensaje}", text_color="#EF4444")

    def validar_y_guardar(self):
        self._limpiar_errores()

        if not self.usuario_editando_id:
            if not hasattr(self, "biometria_temp") or self.biometria_temp is None:
                print("Error: Debes registrar biometrÃ­a primero")
                self.btn_biometria.configure(
                    text=AppContext.t("BiometrÃ­a requerida"),
                    fg_color="#EF4444", hover_color="#DC2626"
                )
                return

        n   = self.inputs_obligatorios.get("Nombres").get().strip()
        em  = self.inputs_obligatorios.get("correo").get().strip()
        cta = self.inputs_obligatorios.get("cuenta").get().strip()

        hay_error = False

        if not n:
            self._mostrar_error("Nombres", "El nombre es obligatorio")
            hay_error = True

        if not cta:
            self._mostrar_error("cuenta", "La cuenta es obligatoria")
            hay_error = True
        elif not cta.isdigit():
            self._mostrar_error("cuenta", "La cuenta solo debe contener nÃºmeros")
            hay_error = True
        elif len(cta) != 8:
            self._mostrar_error("cuenta", f"La cuenta debe tener 8 dÃ­gitos (actualmente tiene {len(cta)})")
            hay_error = True

        if em and "@" not in em:
            self._mostrar_error("correo", "El correo debe contener @")
            hay_error = True

        if hay_error:
            return

        if existe_cuenta(cta, self.usuario_editando_id):
            self._mostrar_error("cuenta", "La cuenta ya estÃ¡ registrada")
            return

        if em and existe_correo(em, self.usuario_editando_id):
            self._mostrar_error("correo", "El correo ya estÃ¡ registrado")
            return

        try:
            id_usuario = self.usuario_editando_id

            if not n or not cta:
                print("Error: Faltan datos:", n, cta, em)
                return

            if em:
                if not re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", em):
                    self._mostrar_error("correo", "Correo invÃ¡lido")
                    return

            if not self.usuario_editando_id and len(cta) != 8:
                return

            ap = self.inputs_apellidos["Apellido Paterno"].get().strip()
            am = self.inputs_apellidos["Apellido Materno"].get().strip()

            if not self.validar_texto_real(n):
                self._mostrar_error("Nombres", "Nombre invÃ¡lido")
                return
            if not self.validar_texto_real(ap):
                self._mostrar_error("Apellido Paterno", "Apellido paterno invÃ¡lido")
                return
            if am and not self.validar_texto_real(am):
                self._mostrar_error("Apellido Materno", "Apellido materno invÃ¡lido")
                return

            n  = n.title()
            ap = ap.title()
            am = am.title()

            TIPOS_USUARIO_INV = {"TRABAJADOR": 1, "SUPERVISOR": 2, "ADMINISTRATIVO": 3}
            tipo_usuario = TIPOS_USUARIO_INV.get(self.rol_var.get().upper())

            carrera_seleccionada = self.carrera_var.get()
            id_carrera = obtener_id_carrera_por_nombre(carrera_seleccionada)
            carreras_validas     = self.carreras_por_plantel.get(self.plantel_menu.get(), [])
            if carrera_seleccionada not in carreras_validas:
                print("Error: Carrera invÃ¡lida")
                return

            id_fac = obtener_id_facultad_por_nombre(self.plantel_menu.get())
            if not id_fac or not tipo_usuario:
                print("Error: tipo_usuario o id_fac invÃ¡lido", tipo_usuario, id_fac)
                return

            if self.usuario_editando_id:
                estado_valor = 1 if self.estado_var.get() else 0
                actualizar_usuario(id_usuario, n, ap, am, cta, tipo_usuario, id_fac, id_carrera, em, estado_valor)
                if hasattr(self, "biometria_temp") and self.biometria_temp is not None:
                    print("Reemplazando biometrÃ­a...")
                    resultado = guardar_encoding(
                        id_usuario,
                        self.biometria_temp,
                        reemplazar=True
                    )

                    if not resultado["ok"]:
                        self.label_estado.configure(
                            text="",
                            text_color="#EF4444"
                        )
                        return

                    encodings_db[:], usuarios_db[:] = cargar_encodings()
                    self.biometria_temp = None

            else:
                if not hasattr(self, "biometria_temp") or self.biometria_temp is None:
                    self.label_estado.configure(
                        text="",
                        text_color="#EF4444"
                    )
                    return

                usuario_id = None
                try:
                    usuario_id = crear_usuario(n, ap, am, tipo_usuario, id_fac, id_carrera, cta, em)
                    if not usuario_id:
                        self.label_estado.configure(
                            text="",
                            text_color="#EF4444"
                        )
                        return

                    resultado = guardar_encoding(usuario_id, self.biometria_temp)

                    if not resultado["ok"]:
                        from app.database.database import get_connection
                        conn = get_connection()
                        conn.cursor().execute("DELETE FROM usuario WHERE id_usuario = ?", (usuario_id,))
                        conn.commit()
                        conn.close()

                        error = resultado.get("error")
                        if error == "rostro_duplicado":
                            dup = resultado.get("usuario_duplicado")
                            self.label_estado.configure(
                                text=f"Error: Este rostro ya pertenece al usuario ID {dup}",
                                text_color="#EF4444"
                            )
                        elif error == "usuario_duplicado":
                            self.label_estado.configure(
                                text="",
                                text_color="#EF4444"
                            )
                        else:
                            self.label_estado.configure(
                                text="",
                                text_color="#EF4444"
                            )

                        self.refresh_data()
                        self.render_table_content(self.all_users)
                        return

                    encodings_db[:], usuarios_db[:] = cargar_encodings()
                    self.biometria_temp = None
                    print("OK: Usuario y biometrÃ­a guardados correctamente")

                except Exception as e:
                    print("ERROR al guardar usuario/biometrÃ­a:", e)
                    if usuario_id:
                        from app.database.database import get_connection
                        conn = get_connection()
                        conn.cursor().execute("DELETE FROM usuario WHERE id_usuario = ?", (usuario_id,))
                        conn.commit()
                        conn.close()
                    self.label_estado.configure(
                        text="",
                        text_color="#EF4444"
                    )
                    return

            self.refresh_data()
            self.render_table_content(self.all_users)
            self.cerrar_formulario()

        except Exception as e:
            print("ERROR AL GUARDAR:", e)

    def cambiar_estado_usuario(self, id_usuario, nuevo_estado):
        try:
            usuario = obtener_usuario_por_id(id_usuario)
            if not usuario:
                print(f"Usuario {id_usuario} no encontrado")
                return
            estado_valor = 1 if nuevo_estado else 0
            actualizar_usuario(
                id_usuario, usuario["nombre"], usuario["a_paterno"],
                usuario["a_materno"], "", usuario["tipo_usuario"],
                usuario["id_facultad"], usuario["id_carrera"], estado_valor
            )
            print(f"OK: Estado del usuario {id_usuario} cambiado a: {'ACTIVO' if estado_valor else 'INACTIVO'}")
            self.refresh_data()
            self.render_table_content(self.all_users)
        except Exception as e:
            print(f"Error: Error al cambiar estado: {e}")

    def cerrar_formulario(self):
        if hasattr(self, "form_base"):
            self.form_base.destroy()
        self.vista_tabla.pack(fill="both", expand=True)
        self.render_table_content(self.all_users)

    def create_header(self, master):
        padx_header = 8 if self.is_compact else 30
        h = ctk.CTkFrame(master, fg_color="transparent")
        h.pack(fill="x", padx=padx_header, pady=(8, 6))

        if self.is_compact:
            ctk.CTkLabel(
                h,
                text=AppContext.t("Personal"),
                font=("Inter", 20, "bold"),
                text_color=COLORS["text"]
            ).pack(anchor="center", pady=(0, 6))
            ctk.CTkButton(
                h,
                text=AppContext.t("Nuevo trabajador"),
                font=self.font_sub, fg_color=COLORS["primary"],
                height=36, corner_radius=8,
                command=self.abrir_formulario
            ).pack(fill="x", padx=8)
        else:
            ctk.CTkLabel(
                h,
                text=AppContext.t("Personal"),
                font=self.font_header,
                text_color=COLORS["text"]
            ).pack(side="left")
            ctk.CTkButton(
                h,
                text=AppContext.t("Nuevo trabajador"),
                font=self.font_sub, fg_color=COLORS["primary"],
                height=40, corner_radius=8,
                command=self.abrir_formulario
            ).pack(side="right")

    def create_search_bar(self, master):
        bar = ctk.CTkFrame(master, fg_color="transparent")
        bar.pack(fill="x", padx=8 if self.is_compact else 30, pady=6)
        self.entry_busqueda = ctk.CTkEntry(
            bar,
            placeholder_text=AppContext.t("Buscar usuario..."),
            height=36 if self.is_compact else 40, corner_radius=8,
            fg_color=COLORS["hover"],
            border_color=COLORS["border"],
            text_color=COLORS["text"]
        )
        self.entry_busqueda.pack(side="left", fill="x", expand=True, padx=(0, 0 if self.is_compact else 15))
        self.entry_busqueda.bind("<KeyRelease>", self.buscar_usuarios)
        self.btn_filter = ctk.CTkButton(
            bar,
            text=AppContext.t("Filtrar âŒµ"),
            width=90 if self.is_compact else 110,
            height=36 if self.is_compact else 40, corner_radius=8,
            fg_color=COLORS["card"], text_color=COLORS["text"],
            border_color=COLORS["border"],
            command=self.toggle_filter
        )
        if self.is_compact:
            self.btn_filter.pack(side="left", padx=(8, 0))
        else:
            self.btn_filter.pack(side="left")

    def buscar_usuarios(self, event=None):
        texto = self.entry_busqueda.get().strip().lower()

        usuarios_filtrados = []
        for u in self.all_users:
            nombre_completo = f"{u['nombre_solo']} {u['ap']} {u['am']}".lower()
            cuenta  = str(u.get("cuenta", "")).lower()
            correo  = str(u.get("correo", "")).lower()
            rol     = str(u.get("r", "")).lower()
            estado  = "activo" if u.get("estado", 1) == 1 else "inactivo"

            if (
                texto in nombre_completo
                or texto in cuenta
                or texto in correo
                or texto in rol
                or texto in estado
            ):
                usuarios_filtrados.append(u)

        if self.filtro_rol_actual != "Todos":
            usuarios_filtrados = [
                u for u in usuarios_filtrados
                if u["r"].upper() == self.filtro_rol_actual.upper()
            ]

        self.render_table_content(usuarios_filtrados)

    def toggle_filter(self):
        if not self.filter_visible:
            self.draw_tags()
            self.filter_container.pack(fill="x", padx=8 if self.is_compact else 30, pady=(0, 15), before=self.main_card)
            self.btn_filter.configure(text=AppContext.t("Filtrar ï¸¿"))
            self.filter_visible = True
        else:
            self.filter_container.pack_forget()
            self.btn_filter.configure(text=AppContext.t("Filtrar âŒµ"))
            self.filter_visible = False

    def draw_tags(self):
        for w in self.filter_container.winfo_children():
            w.destroy()
        r1 = ctk.CTkFrame(self.filter_container, fg_color="transparent")
        r1.pack(fill="x", padx=8 if self.is_compact else 20)
        ctk.CTkLabel(
            r1,
            text=AppContext.t("Rol:"),
            font=self.font_small, text_color=COLORS["text"], width=52 if self.is_compact else 80
        ).pack(side="left")
        # -- CorrecciÃ³n: todos los roles pasan por AppContext.t() --
        for t in ["Todos", "TRABAJADOR", "SUPERVISOR", "ADMINISTRATIVO"]:
            act = self.filtro_rol_actual == t
            ctk.CTkButton(
                r1,
                text=AppContext.t(t),
                height=28, corner_radius=10,
                fg_color=COLORS["hover"] if act else "white",
                text_color=COLORS["text"], border_color=COLORS["border"],
                command=lambda v=t: self.aplicar_filtro_visual(v)
            ).pack(side="left", padx=3)

    def aplicar_filtro_visual(self, v):
        self.filtro_rol_actual = v
        self.draw_tags()
        self.buscar_usuarios()

    def update_carreras_dinamicas(self, fn):
        c = self.carreras_por_plantel.get(fn, ["Sin Carreras"])
        self.carrera_menu.configure(values=c)
        self.carrera_var.set(c[0])

    def abrir_terminal_biometrica(self):
        self._limpiar_errores()

        nombres = self.limpiar_texto(self.inputs_obligatorios["Nombres"].get())
        cuenta  = self.inputs_obligatorios["cuenta"].get().strip()
        correo  = self.inputs_obligatorios["correo"].get().strip()
        ap      = self.limpiar_texto(self.inputs_apellidos["Apellido Paterno"].get())
        am      = self.limpiar_texto(self.inputs_apellidos["Apellido Materno"].get())

        hay_error = False

        if not self.validar_texto_real(nombres):
            self._mostrar_error("Nombres", "El nombre solo debe contener letras")
            hay_error = True
        if not self.validar_texto_real(ap):
            self._mostrar_error("Apellido Paterno", "Apellido paterno invÃ¡lido")
            hay_error = True
        if am and not self.validar_texto_real(am):
            self._mostrar_error("Apellido Materno", "Apellido materno invÃ¡lido")
            hay_error = True
        if not cuenta:
            self._mostrar_error("cuenta", "La cuenta es obligatoria")
            hay_error = True
        elif not cuenta.isdigit():
            self._mostrar_error("cuenta", "La cuenta solo debe contener nÃºmeros")
            hay_error = True
        elif len(cuenta) != 8:
            self._mostrar_error("cuenta", "La cuenta debe tener exactamente 8 nÃºmeros")
            hay_error = True
        if correo and not re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", correo):
            self._mostrar_error("correo", "Correo electrÃ³nico invÃ¡lido")
            hay_error = True

        if hay_error:
            self.btn_biometria.configure(
                text=AppContext.t("Corrige los datos primero"),
                fg_color="#EF4444", hover_color="#DC2626"
            )
            return

        self.btn_biometria.configure(
            text=AppContext.t("Abriendo cÃ¡mara..."),
            fg_color="#0EA5E9"
        )
        self.form_base.pack_forget()

        self.terminal_container = ctk.CTkFrame(self, fg_color="black")
        self.terminal_container.pack(fill="both", expand=True)

        self.terminal_view = TerminalView(
            self.terminal_container,
            user_id=self.usuario_editando_id,
            on_back=self.cerrar_terminal_biometrica,
            on_capture=self.recibir_biometria,
            modo="registro"
        )
        self.terminal_view.pack(fill="both", expand=True)

    def cerrar_terminal_biometrica(self):
        if hasattr(self, "terminal_view"):
            try:
                self.terminal_view.on_close()
            except Exception:
                pass
        if hasattr(self, "terminal_container"):
            self.terminal_container.destroy()

        self.form_base.pack(fill="both", expand=True)

        if not hasattr(self, "biometria_temp") or self.biometria_temp is None:
            self.btn_biometria.configure(
                text=AppContext.t("Registrar BiometrÃ­a"),
                fg_color="#0EA5E9",
                hover_color="#0284C7"
            )

    def recibir_biometria(self, encoding):
        print("OK: Muestras biometricas recibidas")
        self.biometria_temp = encoding

        if hasattr(self, "btn_biometria"):
            self.btn_biometria.configure(
                text=f"{len(encoding)} muestras biometricas registradas",
                fg_color="#10B981",
                hover_color="#059669"
            )

        self.cerrar_terminal_biometrica()
